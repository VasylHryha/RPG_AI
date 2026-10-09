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
// Reuse the host parser's scalar/escape rules, but allocate object layouts once
// rather than caching every insertion prefix. The caller owns these layouts
// until all request JSON has been swept, including the exception path.
struct BoundedParser : js::Parser {
 FrameLayouts& layouts;
 BoundedParser(const std::string& text,FrameLayouts& owner):js::Parser{text},layouts(owner){}
 js::V value(){
  char c=peek();
  if(c=='{'){
   ++i;std::vector<std::pair<std::string,js::V>> fields;std::unordered_map<std::string,size_t> offsets;
   if(peek()=='}'){++i;return layouts.object(fields);}
   do{auto key=string();expect(':');auto v=value();auto entry=offsets.emplace(key,fields.size());
    if(entry.second)fields.emplace_back(std::move(key),v);else fields[entry.first->second].second=v;
    if(peek()=='}'){++i;return layouts.object(fields);}expect(',');}while(true);
  }
  if(c=='['){++i;js::Args a;if(peek()==']'){++i;return js::arr(std::move(a));}
   do{a.push_back(value());if(peek()==']'){++i;return js::arr(std::move(a));}expect(',');}while(true);
  }
  return js::Parser::value();
 }
};
inline js::V parseBounded(const std::string& text,FrameLayouts& layouts){
 BoundedParser parser(text,layouts);auto v=parser.value();
 if(parser.peek())throw std::runtime_error("trailing JSON input");return v;
}
}
