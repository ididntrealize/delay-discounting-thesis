class Util :
    def data_extracted(self, var):
        try :
            var
        except NameError :
            print("Please run the previous block of code first!")
            return False
        else : 
            return var