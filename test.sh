register_nodes()
{
# HACK write to file for POST data bc can't put $1 in a 'string literal'
  echo '{"nodes":["http://0.0.0.0:' > tmp.json
  echo $1 >> tmp.json
  echo '"]}' >> tmp.json
  curl -s -H "Content-Type: application/json" -X POST -d @tmp.json 0.0.0.0:$2/nodes/register > /dev/null
  rm tmp.json
}
check_diff()
{
if [ "$(diff $1 $2)" != "" ]
then
  echo they differ
else
  echo they are the same
fi
}

# SETUP
echo ~~ Mining and transacting with 0.0.0.0:$1 ~~
curl -H "Content-Type: application/json" -X POST -d '{"sender":"me", "recipient":"thing 1", "amount":"1"}' 0.0.0.0:$1/transactions/new
curl -H "Content-Type: application/json" -X POST -d '{"sender":"me", "recipient":"thing 2", "amount":"2"}' 0.0.0.0:$1/transactions/new
curl 0.0.0.0:$1/mine

echo ~~ Mining and transacting with 0.0.0.0:$2 ~~
curl -H "Content-Type: application/json" -X POST -d '{"sender":"thing 1", "recipient":"thing 2", "amount":"1"}' 0.0.0.0:$2/transactions/new
curl 0.0.0.0:$2/mine
curl 0.0.0.0:$2/mine

# CHECK
printf "Comparing blockchains for 0.0.0.0:$1 and 0.0.0.0:$2..."
curl -s 0.0.0.0:$1/chain > chain1
curl -s 0.0.0.0:$2/chain > chain2
check_diff chain1 chain2

# SYNC
printf "Syncing 0.0.0.0:$1..."
register_nodes $1 $2
curl -s 0.0.0.0:$1/nodes/resolve | grep message
printf "Syncing 0.0.0.0:$2..."
register_nodes $2 $1
curl -s 0.0.0.0:$1/nodes/resolve | grep message

# CHECK
printf "Comparing blockchains for 0.0.0.0:$1 and 0.0.0.0:$2..."
curl -s 0.0.0.0:$1/chain > chain1
curl -s 0.0.0.0:$2/chain > chain2
check_diff chain1 chain2
rm chain1 chain2
