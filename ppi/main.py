import os, sys
import appnope
from session import PRSession

def main():

    # subject_initials = str(raw_input('Your initials: '))
    # index_number = int(raw_input('Which run: '))
    # version_number = int(raw_input('Version: ') )

    subject_initials = 'jg'
    index_number = 1
    version_number = 1
    tracker_on = 1

    
    screen_params = {'size':(1920,1080), 'full_screen': True, 'background_color':(0.5, 0.5, 0.5)}
    # screen_params = {'size':(800,600), 'full_screen': False, 'background_color':(0.5, 0.5, 0.5)}
    
    appnope.nope()

    ts = PRSession(subject_initials=subject_initials, index_number=index_number, version_number=version_number, 
                    tracker_on=tracker_on, **screen_params)
    ts.run()

    # autmatically move files:
    if not os.path.exists('data/{}/'.format(subject_initials)):
        os.makedirs('data/{}/'.format(subject_initials))
    os.system('mv %s %s' % (ts.output_file + '.edf', 'data/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '.edf'))
    os.system('mv %s %s' % (ts.output_file + '.tsv', 'data/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '.tsv'))
    os.system('mv %s %s' % (ts.output_file + '_outputDict.pkl', 'data/' + subject_initials + '/' + os.path.split(ts.output_file)[1] + '_outputDict.pkl'))

if __name__ == '__main__':
    main()
