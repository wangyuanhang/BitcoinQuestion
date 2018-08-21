
import time
import json
from urllib.request import urlopen

# method to extract JSON data from given endpoint
def extractJsonFromUrl():
	try:
		url ="https://www.bitmex.com/api/v1/instrument/compositeIndex?symbol=.XBT&filter=%7B%22timestamp.time%22%3A%2210%3A55%3A00%22%2C%22reference%22%3A%22BSTP%22%7D&count=100&reverse=true"
		data = urlopen(url).read()
		return data
	except Exception as e:
		print(e)


# write the final output to a JSON file
def writeJsonFile(fileData):
	file = open("result.json","w")
	file.write(fileData)
	file.close()


# convert bitcoin data to required data format
def output(bitcoin):
    # convert bytes type to json
    data = json.loads(bitcoin.decode("utf-8"))
    # set initial value for lastPrice, highSinceStart, lowSinceStart
    lastPrice = data[len(data)-1]["lastPrice"] # record last day price to calculate the price change
    highSinceStart = data[len(data)-1]["lastPrice"]
    lowSinceStart = data[len(data)-1]["lastPrice"]
    result = [] # collect the final result
    # parse the data in reversed order so that oldest date will be the first data
    for num in range(1, len(data)):
        index = len(data) - num
        temp = {}
        temp["date"] = data[index]["timestamp"]
        temp["price"] = data[index]["lastPrice"]
        if temp["price"] > lastPrice:
            temp["priceChange"] = "UP"
            temp["lowSinceStart"] = lowSinceStart
            # highSinceStart is possible to be updated only when price goes higher than last day
            if data[index]["lastPrice"] > highSinceStart:
                temp["highSinceStart"] = data[index]["lastPrice"]
                highSinceStart = data[index]["lastPrice"]
            else:
                temp["highSinceStart"] = highSinceStart
        elif temp["price"] == lastPrice:
            temp["priceChange"] = "SAME"
            temp["highSinceStart"] = highSinceStart
            temp["lowSinceStart"] = lowSinceStart
        else:
            temp["priceChange"] = "DOWN"
            temp["highSinceStart"] = highSinceStart
            # lowSinceStart is possible to be updated only when price goes lower than last day
            if data[index]["lastPrice"] < lowSinceStart:
                temp["lowSinceStart"] = data[index]["lastPrice"]
                lowSinceStart = data[index]["lastPrice"]
            else:
                temp["lowSinceStart"] = lowSinceStart
        temp["change"] = round(temp["price"] - lastPrice, 2)
        # update lastPrice to current price after calculation
        lastPrice = data[index]["lastPrice"]
        temp["dayOfWeek"] = convertDateToWeekDay(data[index]["timestamp"])
        # append temp to result
        result.append(temp)
    result[0]["change"] = "na"
    result[0]["priceChange"] = "na"
    return result


# Convert date time to the day of week
def convertDateToWeekDay(date):
    weekday = time.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")
    return time.strftime("%A", weekday)


# main method to execute the program
results = output(extractJsonFromUrl())
writeJsonFile(json.dumps(results))