from twilio.rest import Client

# Twilio credentials
account_sid = 'YOUR_ACCOUNT_SID'  # Your Account SID from www.twilio.com/console
auth_token = 'YOUR_AUTH_TOKEN'      # Your Auth Token from www.twilio.com/console
twilio_whatsapp_number = 'whatsapp:+YOUR_TWILIO_WHATSAPP_NUMBER'  # Twilio WhatsApp number

# Create a Twilio client
client = Client(account_sid, auth_token)

def send_whatsapp_message(to_number, message):
    try:
        message = client.messages.create(
            body=message,
            from_=twilio_whatsapp_number,
            to=f'whatsapp:{to_number}'  # Replace with your personal WhatsApp number
        )
        print(f'Message sent: {message.sid}')
    except Exception as e:
        print(f'Error: {e}')




def messenger(request,id):
    chatboard = Conversation.objects.filter(forum_id=id)
    # get or create conversation:
    context={
        'chatboard':chatboard,    
    }  
    return render(request, 'messenger.html', context)


def send(request):
    user = User.objects.get(username = request.user.username)
    room = request.POST['forum.id']
    message= request.POST['message']
    new_message = Message()
    # new_message.forum = Message.objects.create(value=message, forum_id =spec)    
    if request.method == 'POST':
        new_message.sender = user
        new_message.forum = spec
        new_message.value = message
        new_message.save()
        return redirect('messenger')
