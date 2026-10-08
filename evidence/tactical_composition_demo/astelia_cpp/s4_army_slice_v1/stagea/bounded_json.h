#pragma once
#include "js_value.h"
// Dynamic ID-key maps must not use appendShape: it caches every prefix, copying
// all keys/index entries at each insertion (quadratic memory, across frames).
// Own one flat layout per dynamic object until the host sweeps its JSON values.
namespace stagea {
struct FrameLayouts {
 std::vector<std::shared_ptr<js::Shape>> owned;
 js::V object(const std::vector<std::pair<std::string,js::V>>& fields){
  auto shape=std::make_shared<js::Shape>();shape->keys.reserve(fields.size());shape->index.reserve(fields.size());
  auto row=js::heap(js::Object::Plain);row.p->props.reserve(fields.size());
  for(const auto& field:fields){auto index=shape->keys.size();
   if(!shape->index.emplace(field.first,index).second)throw std::invalid_argument("duplicate dynamic JSON key");
   shape->keys.push_back(field.first);auto hot=js::hotLookup.find(field.first);
   if(hot!=js::hotLookup.end())shape->hot[hot->second]=int(index);
   row.p->props.push_back(field.second);
  }
  row.p->shape=shape.get();owned.push_back(std::move(shape));return row;
 }
 void clear(){owned.clear();}
};
}
