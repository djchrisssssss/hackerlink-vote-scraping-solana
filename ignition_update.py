import json
import requests
import math
from time import sleep
from datetime import datetime

Voteaccount = "3rXHdF7CfwG6K2VVFpvBRwdbRwyR5Zn7kQhLgxn4mjk7"
rpcurl = 'https://api.mainnet-beta.solana.com'

headers = {'Content-Type': 'application/json'}

backuppath = open('ignition_list.json', 'r')

pathtxnew = 'ignition_asia_tx_new.txt'
pathtxold = 'ignition_asia_tx.txt'
newtxfile = open(pathtxnew, 'w+')


def noneto0(num):
    try:
        num = int(num)
    except TypeError:
        num = 0
    return num


def countvoteusdc(votingreq, tx):
    outarr = []
    if "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" in votingreq.text:  # If this tx voted USDC for Scallop
        voteresponsejson = json.loads(votingreq.text)
        voteraddress = voteresponsejson["result"]["transaction"]["message"]["accountKeys"][0]
        # need to use "amount" * 1/1000000 cuz if using "uiAmount" it won't count decimals.
        voterusdcbefore = noneto0(
            voteresponsejson["result"]["meta"]["preTokenBalances"][0]["uiTokenAmount"]["amount"])
        voterusdcafter = noneto0(
            voteresponsejson["result"]["meta"]["postTokenBalances"][0]["uiTokenAmount"]["amount"])
        voterusdc = voterusdcbefore - voterusdcafter
        outarr.append([[voteraddress, voterusdc], [tx]])
        txtout = voteraddress, voterusdc*math.pow(10, -6), tx
        print(txtout, file=newtxfile)

def main():

    with backuppath as f:
        listjson = json.load(f)

    newesttx = listjson[0]['signature']

    today = datetime.now()
    print(today.strftime("%Y-%m-%d %H:%M:%S"))

    data = '{"jsonrpc":"2.0","id": 1, "method":"getSignaturesForAddress", "params":["' + Voteaccount + '",{"limit":1000, "until":"'+ newesttx +'"}]}'

    req = requests.post(rpcurl, headers=headers, data=data)
    reqjson = json.loads(req.text)

    if len(reqjson["result"]) != 0:

        for i in range(0, len(reqjson["result"])):

            tx = reqjson["result"][i]["signature"]

            # Only count success transaction.
            if reqjson["result"][i]["err"] == None:
                data = '{"jsonrpc":"2.0","method":"getTransaction","id": 1,"params":["' + tx + '","json"]}'
                datajson = json.loads(data)
                datajson["params"][0] = tx
                data = json.dumps(datajson)
                # Send new req for details.
                votingreq = requests.post(
                    rpcurl, headers=headers, data=data)
                sleep(0.2)
                # print(votingreq.text)
                countvoteusdc(votingreq, tx)

    newtxfile.close()

if __name__ == "__main__":
    main()