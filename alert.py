import winsound
 
freq = 100
dur = 50
 
# loop iterates 5 times i.e, 5 beeps will be produced.
for i in range(0, 5):    
    winsound.Beep(freq, dur)    
    freq+= 100
    dur+= 50

print('hello world')