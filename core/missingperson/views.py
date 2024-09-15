from django.shortcuts import render,redirect
from .models import* 
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime
import face_recognition
import cv2
import requests
from twilio.rest import Client
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from json import load, loads
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

# def match(self,to):
    # # fetch pid based on selection on the tree
    # selected_item = self.tree.selection()[0]
    # pid = self.tree.item(selected_item)["values"][self.tree_d["pid"]]

    # # fetch the details of the person
    # msg_tmplt = f"Hello We have located the missing person, please visit us to verify.\n\nThank you."
    # response = self.send__sms(to, msg_tmplt)

#Add yourr own credentials
account_sid = 'AC32c46895306e6861330691024253e2ba'
auth_token = '24ecfc9691ae2ee38ffb4ce82738acc5'
twilio_whatsapp_number = '+12567332362'

# Create your views here.
def home(request):
    return render(request,"index.html")

 
def detect_from_video(request):
    if request.method == 'POST' and request.FILES['video']:
        # Get the uploaded video file
        video_file = request.FILES['video']
        
        # Save the file to the media directory
        fs = FileSystemStorage()
        video_path = fs.save(video_file.name, video_file)
        video_full_path = os.path.join(settings.MEDIA_ROOT, video_path)

        # Open the uploaded video file for processing
        video_capture = cv2.VideoCapture(video_full_path)

        # Initialize a flag to track if a face has been detected in the video
        face_detected = False

        # Iterate over video frames
        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                break  # Stop if the video has ended

            # Find face locations and encodings in the current frame
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
                # Compare detected face with stored face images
                for person in MissingPerson.objects.all():
                    stored_image = face_recognition.load_image_file(person.image.path)
                    stored_face_encoding = face_recognition.face_encodings(stored_image)[0]

                    # Compare face encodings using a tolerance value
                    matches = face_recognition.compare_faces([stored_face_encoding], face_encoding)

                    if any(matches):
                        name = person.first_name + " " + person.last_name

                        # Highlight the matched face in the frame
                        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                        if not face_detected:
                            # Log detection and notify relevant authorities
                            current_time = datetime.now().strftime('%d-%m-%Y %H:%M')
                            subject = 'Missing Person Found'
                            from_email = 'pptodo01@gmail'
                            recipient_email = person.email
                            recipient_phone_number = '+91' + str(person.phone_number)
                            context = {
                                "first_name": person.first_name,
                                "last_name": person.last_name,
                                "fathers_name": person.father_name,
                                "aadhar_number": person.aadhar_number,
                                "missing_from": person.missing_from,
                                "date_time": current_time,
                                "location": "India"
                            }
                            msg_tmplt = (
                                f"Dear {context['fathers_name']},\n\n"
                                f"We are pleased to inform you that the missing person missing from {context['missing_from']} and you were concerned about has been found. "
                                "The person was located in a camera footage, and we have identified their whereabouts.\n\n"
                                "Here are the details:\n"
                                f" - Name: {context['first_name']} {context['last_name']}\n"
                                f" - Date and Time of Sighting: {context['date_time']}\n"
                                f" - Location: {context['location']}\n"
                                f" - Aadhar Number: {context['aadhar_number']}\n\n"
                                "Thank you for your cooperation and concern in this matter.\n\n"
                            )
                            response = send__sms(recipient_phone_number, msg_tmplt)
                            face_detected = True  # Set the flag to indicate face detection
                            break

            # Break the loop if the face has been detected and processed
            if face_detected:
                break

        video_capture.release()
        cv2.destroyAllWindows()

        # Remove the video file from the server after processing
        fs.delete(video_path)

        # Return to the same page with a message
        message = 'Face detected and processed successfully.' if face_detected else 'No face detected in the video.'
        return render(request, 'upload_video.html', {'message': message, 'face_detected': face_detected})

    return render(request, 'upload_video.html')
def detect(request):
    video_capture = cv2.VideoCapture(0)
    
    # Initialize a flag to track if a face has been detected in the current video stream
    face_detected = False
    
    while True:
        ret, frame = video_capture.read()
        
        # Find face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            # Compare detected face with stored face images
            for person in MissingPerson.objects.all():
                stored_image = face_recognition.load_image_file(person.image.path)
                stored_face_encoding = face_recognition.face_encodings(stored_image)[0]

                # Compare face encodings using a tolerance value
                #tolerance = 0.6  # Adjust this tolerance as needed
                matches = face_recognition.compare_faces([stored_face_encoding], face_encoding)

                if any(matches):
                    name = person.first_name + " " + person.last_name
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                    # Check if a face has already been detected in this video stream
                    if not face_detected:
                        print("Hi " + name + " is found")
                        
                        current_time = datetime.now().strftime('%d-%m-%Y %H:%M')
                        subject = 'Missing Person Found'
                        from_email = 'pptodo01@gmail'
                        recipientmail = person.email
                        recipient_phone_number = '+91'+str(person.phone_number)
                        print(recipient_phone_number)
                        context = {"first_name":person.first_name,"last_name":person.last_name,
                                    'fathers_name':person.father_name,"aadhar_number":person.aadhar_number,
                                    "missing_from":person.missing_from,"date_time":current_time,"location":"India"}
                        #send_wapmessage(context,current_time,wapnum)
                        # send_whatsapp_message(recipient_phone_number, context)
                        # match(recipient_phone_number)
                        # msg_tmplt = f"Hello We have located the missing person, please visit us to verify.\n\nThank you."
                        # response = send__sms(recipient_phone_number)
                        msg_tmplt = (
    f"Dear {context['fathers_name']},\n\n"
    f"We are pleased to inform you that the missing person missing from {context['missing_from']} and you were concerned about has been found. "
    "The person was located in a camera footage, and we have identified their whereabouts.\n\n"
    "Here are the details:\n"
    f" - Name: {context['first_name']} {context['last_name']}\n"
    f" - Date and Time of Sighting: {context['date_time']}\n"
    f" - Location: {context['location']}\n"
    f" - Aadhar Number: {context['aadhar_number']}\n\n"
    #"We understand the relief this news must bring to you. If you have any further questions or require more information, please do not hesitate to reach out to us.\n\n"
    "Thank you for your cooperation and concern in this matter.\n\n")
                        # Pass both phone number and message body to send__sms
                        response = send__sms(recipient_phone_number, msg_tmplt)
                        html_message = render_to_string('findemail.html',context = context)
                        # Send the email
                        #send_mail(subject,'', from_email, [recipientmail], fail_silently=False, html_message=html_message)
                        face_detected = True  # Set the flag to True to indicate a face has been detected
                        break  # Break the loop once a match is found

            # Check if no face was detected in the current frame
            if not face_detected:
                name = "Unknown"
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Camera Feed', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    video_capture.release()
    cv2.destroyAllWindows()
    return render(request, "surveillance.html")

def surveillance(request):
    return render(request,"surveillance.html")

def regmail(request):
    return render(request, 'regmail.html')
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        father_name = request.POST.get('fathers_name')
        date_of_birth = request.POST.get('dob')
        address = request.POST.get('address')
        phone_number = request.POST.get('phonenum')
        aadhar_number = request.POST.get('aadhar_number')
        missing_from = request.POST.get('missing_date')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        gender = request.POST.get('gender')
        aadhar = MissingPerson.objects.filter(aadhar_number=aadhar_number)
        if aadhar.exists():
            messages.info(request, 'Aadhar Number already exists')
            return redirect('/register')
        person = MissingPerson.objects.create(
            first_name = first_name,
            last_name = last_name,
            father_name = father_name,
            date_of_birth = date_of_birth,
            address = address,
            phone_number = phone_number,
            aadhar_number = aadhar_number,
            missing_from = missing_from,
            email = email,
            image = image,
            gender = gender,
        )
        person.save()
        messages.success(request,'Case Registered Successfully')
        current_time = datetime.now().strftime('%d-%m-%Y %H:%M')
        subject = 'Case Registered Successfully'
        from_email = 'pptodo01@gmail'
        recipientmail = person.email
        context = {"first_name":person.first_name,"last_name":person.last_name,
                    'fathers_name':person.father_name,"aadhar_number":person.aadhar_number,
                    "missing_from":person.missing_from,"date_time":current_time}
        html_message = render_to_string('regmail.html',context = context)
        # Send the email
        # send_mail(subject,'', from_email, [recipientmail], fail_silently=False, html_message=html_message)
        return render(request,"regmail.html",context)

    return render(request,"register.html")

# def send__sms(self, to):
#     to = f"+91{to}" if len(str(to)) == 10 else f"+{to}"
#     tw_creds = loads(open('creds.json').read())["twilio"]

#     account_sid, auth_token = tw_creds["sid"], tw_creds["token"]
#     client = Client(account_sid, auth_token)

#     message = client.messages.create(
#         from_=tw_creds['from_'],
#         # body=body,
#         to=to
#     )
#     return message.sid

def send__sms(to, body):
    to = f"+91{to}" if len(str(to)) == 10 else f"+{to}"
    tw_creds = loads(open('creds.json').read())["twilio"]

    account_sid, auth_token = tw_creds["sid"], tw_creds["token"]
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=tw_creds['from_'],
        body=body,  # Pass the message body
        to=to
    )
    return message.sid


def  missing(request):
    queryset = MissingPerson.objects.all()
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(aadhar_number__icontains=search_query)
    
    context = {'missingperson': queryset}
    return render(request,"missing.html",context)

def delete_person(request, person_id):
    person = get_object_or_404(MissingPerson, id=person_id)
    person.delete()
    return redirect('missing')  # Redirect to the missing view after deleting


def update_person(request, person_id):
    person = get_object_or_404(MissingPerson, id=person_id)

    if request.method == 'POST':
        # Retrieve data from the form
        first_name = request.POST.get('first_name', person.first_name)
        last_name = request.POST.get('last_name', person.last_name)
        fathers_name = request.POST.get('fathers_name', person.fathers_name)
        dob = request.POST.get('dob', person.dob)
        address = request.POST.get('address', person.address)
        email = request.POST.get('email', person.email)
        phonenum = request.POST.get('phonenum', person.phonenum)
        aadhar_number = request.POST.get('aadhar_number', person.aadhar_number)
        missing_date = request.POST.get('missing_date', person.missing_date)
        gender = request.POST.get('gender', person.gender)

        # Check if a new image is provided
        new_image = request.FILES.get('image')
        if new_image:
            person.image = new_image

        # Update the person instance
        person.first_name = first_name
        person.last_name = last_name
        person.fathers_name = fathers_name
        person.dob = dob
        person.address = address
        person.email = email
        person.phonenum = phonenum
        person.aadhar_number = aadhar_number
        person.missing_date = missing_date
        person.gender = gender

        # Save the changes
        person.save()

        return redirect('missing')  # Redirect to the missing view after editing

    return render(request, 'edit.html', {'person': person})
