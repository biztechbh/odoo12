#/etc/python3
import sys
import base64
import cups

printing_queue = []

#Adding elements to queue
def enqueue(data):
    if data not in printing_queue:
        printing_queue.insert(0, data)
        return True
    return False

#Removing the last element from the queue
def dequeue():
    print_file = []
    if len(printing_queue)>0:
        print_file = printing_queue[-1]
        printing_queue.remove(printing_queue[-1])
        return print_file
    return ("Queue Empty!")

def make_pdf(data, printer) :
    f = open('/tmp/temp.pdf', 'wb')
    f.write(base64.b64decode(data))
    enqueue([printer, f.name])
    print_data = dequeue()
    if print_data:
        connection = cups.Connection(host='localhost', port=631)
        connection.printFile(print_data[0], print_data[1], print_data[1], options={'InputSlot': 'Auto'})
    return True

if __name__ =='__main__':
    make_pdf = make_pdf(sys.argv[1], sys.argv[2])


