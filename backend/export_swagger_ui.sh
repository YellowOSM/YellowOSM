# workaround for swagger-ui
# responder has issues with the built-in swagger-ui behind a reverse proxy
# it does not serve "schema.yml", it serves "/schema.yml"...
# 
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# echo ${BASH_SOURCE[0]}
echo `pwd`
cd $DIR
echo `pwd`
# PWD=`pwd`
wget -r 0.0.0.0:5000/api/docs 
# echo $?
if [ $? == "4" ]; then
  echo -e "\nrun backend on port 5000, please."; exit -1; fi

rm -r ../static/api-docs
mv 0.0.0.0:5000 ../static/api-docs
cd ../static/api-docs 
mv api/docs index.html 
rm -r api
wget 0.0.0.0:5000/schema.yml -O schema.yml
exit
