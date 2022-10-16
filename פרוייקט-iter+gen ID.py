#!/usr/bin/env python
# coding: utf-8

# In[1]:


class IDiterator:
   
    def __init__(self, _id):
        """initiates class instances with ID number.
        :param _id: ID number
        :type _id: int
        :return: None
        """
        self._id = _id
        self.lst = []
        self.lst2 = [[]]
        
    def __iter__(self):
        return self
    
    def check_id_valid(self):
        """checks validity of ID input.
        :return: boolean
        """
        # sorting and appending the ID number input into a list
        self.lst2.append([])
        for index, num in enumerate(str(self._id)):   
            if(index+1) % 2 == 0:
                self.lst.append(int(num)*2)
            else:
                self.lst.append(int(num))
        # sorting and appending the ID number input into a second nested list        
        for num in self.lst:
            if num > 9:
                count = 0
                for digit in str(num):
                    count += int(digit)
                self.lst2[1].append(count)
            else:
                self.lst2[1].append(num)
        # clearing the two lists to have them ready for the next iteration         
        self.lst.clear()
        self.lst2.remove(self.lst2[0])
        return True if sum(self.lst2[0]) % 10 == 0 else False

    def __next__(self):
        """iterates over ID numbers in range(input,999999999).
        :return: valid ID numbers
        :rtype: iterator
        """
        self._id += 1
        if self._id == 999999999:
            raise StopIteration
        if self.check_id_valid():
            return self._id
       
        


# In[2]:


lst = []
lst2 = [[]]


def id_generator(id_num):
    """checks validity of ID input.
    :param id_num: ID number input
    :type id_num: int
    :yield: valid ID number
    :ytype: iterator
    """
    for i in range(id_num,999999999): 
        id_num += 1
        lst2.append([])
        for index, num in enumerate(str(id_num)):
            if(index+1) % 2 == 0:
                lst.append(int(num)*2)
            else:
                lst.append(int(num))
        for num in lst:
            if num > 9:
                count = 0
                for digit in str(num):
                    count += int(digit)
                lst2[1].append(count)
            else:
                lst2[1].append(num)
            
        lst.clear()
        lst2.remove(lst2[0])
        
        if sum(lst2[0]) % 10 == 0:
                yield id_num
                
             
               


# In[3]:


Enter_ID = int(input("Please choose a number  :"))
Choose_Gen_or_Iter = input("Generator or Iterator? (gen/it)?  ") 
id_number = iter(IDiterator(Enter_ID))
generator = id_generator(Enter_ID)

def main():
    if Choose_Gen_or_Iter == "gen":
        print("")
        print("YOU CHOSE GENERATOR..@")
        count = 0
        for num in generator:
            count += 1
            print(num)     
            if count == 10:
                break
        
                
                
    elif Choose_Gen_or_Iter == "it":
        print("")
        print("YOU CHOSE ITERATOR..=>")
        count = 0
        for num in id_number:
            if num is not None:
                count += 1
                print(num)     
            if count == 10:
                break
        
if __name__ == "__main__":
    main()   


# In[ ]:




