def registration():
    print("\nREGISTRATION")
    print("------------------------------")
    TO = "whatsapp:+91" + input("Enter your phone number: ")
    NAME = input("Enter your name: ")
    print("In order to use this service, send the message \"join crowd-pie\" to " + secret.FROM.split(":")[1] + " on whatsapp")
    print("\n")

    try: 
        client.messages.create(body="Hello " + NAME + "!", from_=secret.FROM, to=TO)
    except:
        print("\nInvalid Whatsapp Number\n")

    time.sleep(5)
    sent = input("\nI have sent the message (y/n): ")
    if sent == 'y':
        print("\nYou would have received a whatsapp message from " + secret.FROM.split(":")[1])
        print("In case you haven't, then it is likely that the registration has failed. Try again")
        print("\n------------------------------\n")
        time.sleep(5)
        return TO
    else:
        print("------------------------------\n")
        registration()

def get_pincodes(pincode_list):
    print("\nEnter the pincodes of the areas for which you want to recieve vaccine availability updates\n")
    while(True):
        pincode = input("PINCODE (enter blank space if there are no more pin codes left to add): ").strip()
        if pincode == "":
            break
        if (len(pincode) != 6) or (re.search("[a-zA-Z]", pincode)) != None or (re.search("[-_=+!@#$%^&*()/.,<>?][{}\|]", pincode)):
            print("\nEnter a valid pincode \n")
            continue
        try:
            pincode_list.append(int(pincode))
        except:
            print("\nEnter a valid pincode \n")
            continue
    return pincode_list

def find_centers(pincode_list, centers):
    for pincode in pincode_list:
        try:
            requestURL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date={date}".format(pincode=pincode, date=date)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            response = requests.get(requestURL, headers=headers)
            new_center_list = response.json()['centers']
            centers += new_center_list
        except:
            print("\nThere was an error while fetching the data\n")
            print("\nIt is likely that " + str(pincode) + " is not a valid pincode\n")
            continue
    return centers


def ignore():
    client.messages.create(body="Hello, Sailesh!", from_=secret.FROM, to="whatsapp:+918660541223")

def find_availability(available_centers, centers):
    if len(centers) == 0:
        return []
    for center in centers:
        for session in center['sessions']:
            if session['available_capacity'] > 0:
                available_centers.append(center)
                break
    return available_centers

def send_message(available_centers):
    if len(available_centers) > 0:
        for center in available_centers:
            for session in center['sessions']:
                if session['available_capacity'] > 0:
                    slots = '\n'.join(session['slots'])
                    fees = center['vaccine_fees'][0]['fee'] if center['fee_type'] == 'Paid' else 'Free'
                    body = "There is a vaccine slot available on {date} at *{address}*, _{name}_. \nPincode: {pincode}\nAge: {age}+\nAvailable slots: {slots}\n Vaccine: {vaccine}\n Fees: {fees}\n\n*Book Now!*\nhttps://www.cowin.gov.in/home".format(date=session['date'], address=center['address'], name=center['name'], pincode=center['pincode'], age=session['min_age_limit'], slots=slots, vaccine=session['vaccine'], fees=fees)
                    toaster.show_toast("Vaccine Available!", body)
                    print(body + '\n')
                    try:
                        client.messages.create(body=body, from_=secret.FROM, to=TO)
                    except:
                        print("\nYour session seems to have expired. Restart the program and follow the instructions.")
                        print("It is likely that there is a slot available and you are not notified about it.\n")
                        return 'SESSION_TIMEOUT'


# array item -> object -> {address, block_name, center_id, district_name, fee_type, from, lat, long, name, pincode, sessions, state_name, to, vaccine_fees}
# sessions -> array -> object -> {available_capacity, date, min_age_limit, session_id, slots, vaccine}
#       slots -> array 
# vaccine_fees -> array -> object -> {fee, vaccine}

if __name__ == "__main__":

    import requests
    from datetime import date
    import secret
    from twilio.rest import Client
    import time
    import re
    from win10toast import ToastNotifier


    client = Client(secret.TWILIO_SID, secret.TWILIO_AUTH_TOKEN)
    toaster = ToastNotifier()

    today = date.today()
    date = today.strftime("%d-%m-%Y")

    pincode_list = []
    centers = []
    available_centers = []
    TO = ''

    TO = registration()
    pincode_list = get_pincodes(pincode_list)

    print("\nPress ctrl+C at anytime to quit the program\n")

    while(True):

        centers = find_centers(pincode_list, [])
        available_centers = find_availability([], centers)
        message = send_message(available_centers)
        if message == 'SESSION_TIMEOUT':
            break
        time.sleep(60)

