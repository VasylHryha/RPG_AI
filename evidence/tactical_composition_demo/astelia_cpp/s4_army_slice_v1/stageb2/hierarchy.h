#pragma once
#include "candidates.h"
namespace stageb2 {
constexpr size_t MEMBERS=64,FAMILY_SLOTS=32;
using Families=std::array<std::vector<size_t>,FAMILY_SLOTS>;
inline Families hierarchy(const std::vector<Candidate>& bank,const std::string& head){
 std::vector<std::pair<int,size_t>> layout=head=="aim"?std::vector<std::pair<int,size_t>>{{0,2},{1,1},{2,1},{3,1}}:std::vector<std::pair<int,size_t>>{{4,1},{5,1},{6,1},{7,1},{8,2},{9,1},{10,3},{18,2},{19,1},{20,1},{21,1},{22,1},{23,6},{24,1},{25,3}};
 Families result;size_t slot=0,seen=0;
 for(auto [type,pages]:layout){std::vector<size_t> indices;for(size_t j=0;j<bank.size();++j)if(bank[j].type==type)indices.push_back(j);
 std::stable_sort(indices.begin(),indices.end(),[&](size_t a,size_t b){return std::floor(bank[a].features[13]*1e8+.5)<std::floor(bank[b].features[13]*1e8+.5);});
 if(indices.size()>pages*MEMBERS)throw std::invalid_argument("hierarchical family overflow");
 for(size_t rank=0;rank<indices.size();++rank)result[slot+rank/MEMBERS].push_back(indices[rank]);seen+=indices.size();slot+=pages;}
 if(seen!=bank.size())throw std::invalid_argument("hierarchy loses candidates");return result;
}
}
