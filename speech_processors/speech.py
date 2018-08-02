import speech_recognition as sr


def recognize_speech_from_mic(recognizer, microphone):

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response


if __name__ == "__main__":
   
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print('command any option : ')
    
    while 1:
        speech = recognize_speech_from_mic(recognizer, microphone)
        cmd = speech["transcription"]
        if speech["transcription"]:
            print("You said: {}".format(cmd))
        if cmd == 'music':
            print('playing music ...')
        elif cmd == 'wheelchair':
            print('controlling wheelchair')
        elif cmd == 'wheelchair':
            print('controlling wheelchair')	
        elif cmd == 'video':
            print('playing video ...')
        elif cmd == 'SMS':
            print('sending sms...')	
        elif cmd == 'message':
            print('sending mail ...')
        elif cmd == 'light':
            print('turning light on/off')
        elif cmd == 'fan':
            print('turning fan on/off')	
        elif cmd == 'start':
            print('starting...')	
        elif cmd == 'left':
            print('turning left ...')
        elif cmd == 'right':
            print('turning right ...')
        elif cmd == 'stop':
            print('stopping...')				
        elif cmd == 'exit':
            break
		
	