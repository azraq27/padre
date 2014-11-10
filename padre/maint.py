def strip_directories(s):
    '''strip fixed leading directories and duplicate files from subjects'''
    new_sess = dict(s.sessions)
    for sess in new_sess:
        for label in new_sess[sess]['labels']:
            new_sess[sess]['labels'][label] = list(set([os.path.basename(x) for x in new_sess[sess]['labels'][label]]))
    s.sessions = new_sess
    s.save()