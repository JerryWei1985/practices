#!/usr/bin/python
from google.protobuf import text_format
import addressbook_pb2 as addressbook
import sys

def PromptForAddress(person):
    person.id = int(raw_input('Enter person ID number: '))
    person.name = raw_input('Enter name: ')

    email = raw_input('Enter email address: ')
    if email != '':
        person.email = email

    while True:
        number = raw_input('Enter a phone number: ')
        if number == '':
            break

        phone_number = person.phones.add()
        phone_number.number = number

        type = raw_input('Is this a mobile, home, or work phone? ')
        if type == 'mobile':
            phone_number.type = addressbook.Person.PhoneType.MOBILE
        elif type == 'home':
            phone_number.type = addressbook.Person.PhoneType.HOME
        elif type == 'work':
            phone_number.type = addressbook.Person.PhoneType.WORK
        else:
            print 'Unknown phone type'

if len(sys.argv) != 2:
    print 'Usage:', sys.argv[0], 'ADDRESS_BOOK_FILE'
    sys.exit(-1)

address_book = addressbook.AddressBook()

try:
    f = open(sys.argv[1], 'rb')
    address_book.ParseFromString(f.read())
    f.close()
except IOError:
    print sys.argv[1] + ': Could not open file. Creating a new one.'

PromptForAddress(address_book.people.add())

f = open(sys.argv[1], 'wb')
text_proto = text_format.MessageToString(address_book)
print text_proto
f.write(address_book.SerializeToString())
f.close()
