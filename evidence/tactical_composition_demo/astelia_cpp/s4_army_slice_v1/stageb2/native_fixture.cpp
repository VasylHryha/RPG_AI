// Zero-combat RPC fixture. The engine has no fight entrypoint here.
#include "stagea.h"
#include "candidates.h"
#include <iostream>
#include <iomanip>
int main(){std::string line;std::cout<<std::setprecision(17);while(std::getline(std::cin,line)){try{auto request=js::parse(line);auto out=stagea::replay(request);std::cout<<js::stringify(out)<<'\n';}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}}
