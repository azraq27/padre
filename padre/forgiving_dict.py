class ForgivingDict(dict):
    '''will return None instead of raising KeyError'''
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self,key)
        except KeyError:
            return None
    
    @classmethod
    def copy_nested_dict(cls,orig_iter):
        '''will iterate through `orig_iter` and convert all dicts objects to ForgivingDict's'''
        if orig_iter.__class__ == dict:
            return_iter = cls()
        else:
            return_iter = []
        if isinstance(orig_iter,dict):
            for i in orig_iter:
                if '__iter__' in dir(orig_iter[i]):
                    return_iter[i] = cls.copy_nested_dict(orig_iter[i])
                else:
                    return_iter[i] = orig_iter[i]
        else:
            for i in orig_iter:
                if '__iter__' in dir(i):
                    return_iter.append(cls.copy_nested_dict(i))
                else:
                    return_iter.append(i)
        if orig_iter.__class__ != dict:
            return_iter = orig_iter.__class__(return_iter)
        return return_iter