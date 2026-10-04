#include "spatial.h"

namespace astelia {
Cell SpatialGrid::coordinate(Vec2 p) const {
  const double x=std::floor(p.x/cellSize_), y=std::floor(p.y/cellSize_);
  // Strict interior bound avoids UB converting rounded doubles at int64 limits.
  constexpr double limit=double(uint64_t(1)<<62);
  if (!std::isfinite(x) || !std::isfinite(y) || std::abs(x)>=limit || std::abs(y)>=limit)
    throw std::invalid_argument("spatial coordinate outside supported range");
  return {int64_t(x),int64_t(y)};
}
SpatialGrid::Bucket& SpatialGrid::bucket(Cell c) {
  if (inside(c)) {
    size_t i=size_t(c.x)*size_t(rows_)+size_t(c.y);
    if (dense_[i].head==invalidSlot) touched_.push_back(i);
    return dense_[i];
  }
  return overflow_[c];
}
const SpatialGrid::Bucket* SpatialGrid::find(Cell c) const {
  if (inside(c)) return &dense_[size_t(c.x)*size_t(rows_)+size_t(c.y)];
  auto it=overflow_.find(c); return it==overflow_.end()?nullptr:&it->second;
}
void SpatialGrid::build(const std::vector<UnitHot>& units,const std::vector<uint32_t>& active,double width,double height,double cellSize) {
  if (!(cellSize>0) || !std::isfinite(cellSize) || !(width>0) || !(height>0) || !std::isfinite(width) || !std::isfinite(height))
    throw std::invalid_argument("invalid spatial dimensions");
  for (auto i:touched_) dense_[i]=Bucket{};
  touched_.clear(); overflow_.clear(); members_.clear(); cellSize_=cellSize; maximumRadius_=0;
  const auto bounds=coordinate({width,height});
  const int64_t cols=bounds.x+1, rows=bounds.y+1;
  constexpr size_t maximumDenseCells=65536;
  const bool dense=cols>0 && rows>0 && static_cast<long double>(cols)*rows<=maximumDenseCells;
  const size_t required=dense?size_t(cols)*size_t(rows):0;
  if (columns_!=cols || rows_!=rows || dense_.size()!=required) dense_.assign(required,Bucket{});
  columns_=cols; rows_=rows;
  next_.resize(units.size(),invalidSlot); previous_.resize(units.size(),invalidSlot);
  locations_.resize(units.size()); memberPosition_.assign(units.size(),invalidSlot); members_.reserve(active.size());
  for (auto i:active) {
    if (i>=units.size()) throw std::logic_error("invalid active slot");
    const auto& u=units[i]; if (u.alive) insert(i,u);
  }
}
void SpatialGrid::insert(uint32_t i,const UnitHot& u) {
  if (!ready()) throw std::logic_error("insert into unbuilt grid");
  validateBody(u); const Cell location=coordinate(u.pos);
  if (!u.alive) throw std::logic_error("insert dead unit into grid");
  if (contains(i)) remove(i);
  const size_t n=size_t(i)+1;
  if (next_.size()<n) {
    next_.resize(n,invalidSlot);previous_.resize(n,invalidSlot);
    locations_.resize(n);memberPosition_.resize(n,invalidSlot);
  }
  maximumRadius_=std::max(maximumRadius_,u.radius);
  memberPosition_[i]=uint32_t(members_.size());members_.push_back(i);
  locations_[i]=location;auto& b=bucket(location);previous_[i]=b.tail;next_[i]=invalidSlot;
  if (b.tail==invalidSlot) b.head=i;else next_[b.tail]=i;
  b.tail=i;
}
void SpatialGrid::remove(uint32_t i) {
  if (!contains(i)) return;
  auto& b=bucket(locations_[i]);
  if (previous_[i]==invalidSlot) b.head=next_[i];else next_[previous_[i]]=next_[i];
  if (next_[i]==invalidSlot) b.tail=previous_[i];else previous_[next_[i]]=previous_[i];
  const uint32_t position=memberPosition_[i],last=members_.back();
  members_[position]=last;memberPosition_[last]=position;members_.pop_back();
  memberPosition_[i]=invalidSlot;next_[i]=previous_[i]=invalidSlot;
}
void SpatialGrid::moved(uint32_t i,Vec2 position) {
  if (!contains(i)) throw std::logic_error("move of unit absent from grid");
  const Cell to=coordinate(position);
  if (to==locations_.at(i)) return;
  auto& old=bucket(locations_[i]);
  if (previous_[i]==invalidSlot) old.head=next_[i]; else next_[previous_[i]]=next_[i];
  if (next_[i]==invalidSlot) old.tail=previous_[i]; else previous_[next_[i]]=previous_[i];
  auto& dest=bucket(to); previous_[i]=dest.tail; next_[i]=invalidSlot;
  if (dest.tail==invalidSlot) dest.head=i; else next_[dest.tail]=i;
  dest.tail=i; locations_[i]=to;
}
UnitRef lineBlocker(const std::vector<UnitHot>& units,const SpatialGrid& grid,Vec2 a,Vec2 b,double targetRadius,UnitRef shooter,UnitRef target) {
  const Vec2 delta=b-a; const double l=length(delta); if (l<1) return {};
  const Vec2 dir=delta*(1/l); double best=l-targetRadius; UnitRef found;
  const double pad=grid.maximumRadius()+1.5;
  grid.query({std::min(a.x,b.x)-pad,std::min(a.y,b.y)-pad},
             {std::max(a.x,b.x)+pad,std::max(a.y,b.y)+pad},[&](uint32_t i) {
    const auto& u=units[i]; UnitRef ref{i,u.generation};
    if (!u.alive || ref==shooter || ref==target) return;
    double t; if (!blockerParameter(a,dir,best,u,t)) return;
    if (t<best || (found && t==best && u.id<units[found.slot].id)) { best=t; found=ref; }
  });
  return found;
}
void separate(std::vector<UnitHot>& units,const std::vector<uint32_t>& active,SpatialGrid& grid,double width,double height,std::vector<Vec2>& pushes) {
  grid.build(units,active,width,height,24);
  pushes.assign(units.size(),Vec2{});
  for (auto i:active) {
    const auto& a=units[i]; if (!a.alive) continue;
    const double reach=a.radius+grid.maximumRadius();
    grid.query({a.pos.x-reach,a.pos.y-reach},{a.pos.x+reach,a.pos.y+reach},[&](uint32_t j) {
      const auto& b=units[j];
      // IDs retain spawn order even when a dead slot is reclaimed.
      if (!b.alive || b.id<=a.id) return;
      const Vec2 d=b.pos-a.pos; const double l=length(d), sum=a.radius+b.radius;
      if (l>=sum || l==0) return;
      const Vec2 push=d*((sum-l)/(2*l));
      pushes[i]=pushes[i]-push; pushes[j]=pushes[j]+push;
    });
  }
  for (auto i:active) if (units[i].alive) {
    auto& u=units[i];
    u.pos={clamp(u.pos.x+pushes[i].x,u.radius,width-u.radius),clamp(u.pos.y+pushes[i].y,u.radius,height-u.radius)};
  }
}
} // namespace astelia
