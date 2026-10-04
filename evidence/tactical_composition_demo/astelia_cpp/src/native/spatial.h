#pragma once
#include "geometry.h"
#include <unordered_map>

namespace astelia {
struct Cell {
  int64_t x=0,y=0;
  friend bool operator==(Cell a,Cell b) { return a.x==b.x && a.y==b.y; }
};
struct CellHash {
  size_t operator()(Cell c) const {
    uint64_t x=uint64_t(c.x), y=uint64_t(c.y);
    x^=x>>30; x*=0xbf58476d1ce4e5b9ULL; x^=x>>27;
    y^=y>>30; y*=0x94d049bb133111ebULL; y^=y>>31;
    return size_t(x^(y+0x9e3779b97f4a7c15ULL+(x<<6)+(x>>2)));
  }
};
// Dense arena buckets and explicit overflow buckets; lists use index links.
// A large arena falls back to sparse coordinates rather than allocating by area.
class SpatialGrid {
  struct Bucket { uint32_t head=invalidSlot, tail=invalidSlot; };
  double cellSize_=40, maximumRadius_=0;
  int64_t columns_=0, rows_=0;
  std::vector<Bucket> dense_;
  std::vector<size_t> touched_;
  std::unordered_map<Cell,Bucket,CellHash> overflow_;
  std::vector<uint32_t> next_, previous_, members_, memberPosition_;
  std::vector<Cell> locations_;
  bool inside(Cell c) const { return !dense_.empty() && c.x>=0 && c.y>=0 && c.x<columns_ && c.y<rows_; }
  Bucket& bucket(Cell c);
  const Bucket* find(Cell c) const;
public:
  void build(const std::vector<UnitHot>& units,const std::vector<uint32_t>& active,double width,double height,double cellSize);
  bool ready() const { return columns_>0 && rows_>0; }
  bool contains(uint32_t index) const { return index<memberPosition_.size() && memberPosition_[index]!=invalidSlot; }
  void insert(uint32_t index,const UnitHot& unit);
  void remove(uint32_t index);
  void moved(uint32_t index,Vec2 position);
  Cell coordinate(Vec2 p) const;
  double maximumRadius() const { return maximumRadius_; }
  // Very long segments use a bounded full-member scan rather than huge cell loops.
  template<class F> void query(Vec2 lo,Vec2 hi,F&& callback) const {
    Cell a=coordinate(lo), b=coordinate(hi);
    const long double nx=static_cast<long double>(b.x)-a.x+1, ny=static_cast<long double>(b.y)-a.y+1;
    if (nx<=0 || ny<=0) return;
    if (nx*ny>4096) { for (auto i:members_) callback(i); return; }
    for (int64_t x=a.x;;++x) {
      for (int64_t y=a.y;;++y) {
        if (const auto* p=find({x,y})) for (auto i=p->head;i!=invalidSlot;i=next_[i]) callback(i);
        if (y==b.y) break;
      }
      if (x==b.x) break;
    }
  }
};
UnitRef lineBlocker(const std::vector<UnitHot>& units,const SpatialGrid& grid,Vec2 a,Vec2 b,double targetRadius,UnitRef shooter,UnitRef target);
void separate(std::vector<UnitHot>& units,const std::vector<uint32_t>& active,SpatialGrid& grid,double width,double height,std::vector<Vec2>& pushes);
} // namespace astelia
