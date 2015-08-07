#!/usr/bin/env python

""" Defines two classes:
- DataElement (contains all information about one word of vocabulary)
- DataSet (a class that bundles all DataElements)"""

# -*- coding: utf-8 -*-

import csv


class DataElement(object):
    """ Contains all information about one word of vocabulary. """
    
    def __init__(self):
        
        # The fields that are to be synchronized with 
        # the anki note. 
        # Should be of type 
        # {"fieldname":"value", ...}
        self.fields = {}

        self.is_dupe = False
        self.is_added = False

    def is_in_queue(self):
        """ Should this element pop up in the current queue 
        of vocabulary that we want to add? """

        return not self.is_dupe and not self.is_added

    def set_fields_hook(self):
        """ Should be run after changes to self.fields were
        made. """
        
        pass


class DataSet(object):
    """ Collects DataElements instances. """

    def __init__(self):
        self._data = []
    
        # The index of the data element which is to be/was
        # imported to Anki.
        self._cursor = 0

    def reverse(self):
        self._data.reverse()
        self._cursor = len(self._data) -1 -self._cursor

    def get_current(self):

        return self._data[self._cursor]

    def reduced_cursor(self):
        i = 0
        for i in range(self._cursor):
            if self._data[i].is_in_queue():
                i += 1
        return i

    def set_current(self, elem):

        self._data[self._cursor] = elem 

    def load(self, filename):
        """ Loads input file to self._data. """
        # todo: configure this loading.

        with open(filename,'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            
            # must match Anki fieldnames. If you want to ignore a field, just set it to ""
            field_names = ["Expression", "Kana", "Translation", None]
    
            for row in reader:
                fields = [c.decode('utf8') for c in row]
                element = DataElement()             
                
                if not len(fields) == len(field_names):
                    raise ValueError, "The number of supplied field_names (%d) doesn't match the number of fields in the file %s (%d)." % (len(field_names), filename, len(fields))
                
                for i in range(len(fields)):
                    element.fields[field_names[i]] = fields[i] 
                
                element.set_fields_hook()
                self._data.append(element)

    # Statistics

    def count_data(self, boolean):
        i = 0
        for entry in self._data:
            if boolean(entry):
                i += 1
        return i



    def len_all(self):
        return self.count_data(lambda e: True)

    def len_added(self):
        return self.count_data(lambda e: e.is_added())

    def len_dupe(self):
        return self.count_data(lambda e: e.is_dupe())
        
    def len_queue(self):
        return self.count_data(lambda e: e.is_in_queue())



    # Navigate with skipping.

    def go(self, func, start=None, dry=False):
        """ Updates self._cursor. 
        Starts with cursor = $start (default: func(self.cursor)
        and repeatedly call cursor = fun(cursor).
        Once the element at cursor is an element that should be in 
        the queue, we set self._cursor = cursor.
        Returns True if self._cursor was changed, False otherwise. 
        If dry == True: self._cursor remains untouched, only the
        return value is given."""
        
        old_cursor = self._cursor
        new_cursor = self._cursor
        
        if start == None:
            # do NOT use "if not start", because start = 0 gets 
            # also evaluated as False.
            start = func(self._cursor)
        
        cursor = start
        
        while cursor in range(len(self._data)):
            print(cursor)
            if self._data[cursor].is_in_queue:
                new_cursor = cursor
                break 
            cursor = func(cursor)
        
        if not dry:
            self._cursor = new_cursor

        return new_cursor == old_cursor

    def go_next(self, dry=False):
        """ Go to next queue element 
        (i.e. sets self._cursor to the index of the next queue element)
        Returns False if we are already at the last queue element.
        If dry == True: self._cursor remains untouched, only the
        return value is given. """
        return self.go(lambda x: x+1, dry=dry)

    def go_previous(self, dry=False):
        """ Go to previous queue element 
        (i.e. sets self._cursor to the index of the previous queue element)
        Returns False if we are already at the first queue element.
        If dry == True: self._cursor remains untouched, only the
        return value is given. """

        return self.go(lambda x: x-1, dry=dry)

    def go_first(self):
        """ Go to first queue element 
        (i.e. sets self._cursor to the index of the first queue element)
        Returns False if we are already at the first queue element. """
        
        return self.go(lambda x: x+1, start=0)
        
    def go_last(self):
        """ Go to last queue element 
        (i.e. sets self._cursor to the index of the last queue element)
        Returns False if we are already at the last queue element. """
        
        return self.go(lambda x: x-1, start=len(self._data)-1)

    def is_go_previous_possible(self):
        return self.go_next(dry=True)

    def is_go_next_possible(self):
        return self.go_previous(dry=True)

    def is_queue_empty(self):
        return self.len_queue() == 0

    def is_in_queue(self):
        """ """
        # todo: make real thing
        return True

        # isque=False
        # if len(exp)>=3: 
        #     if exp in current.fields['Expression']:
        #         isque=True
        # else:
        #     print(exp,current[0],exp==current[0].split(self.delim)[-1])
        #     if exp==current[0].split(self.delim)[-1]:
        #         isque=True