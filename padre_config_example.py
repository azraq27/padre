import os
import padre as p

rsync = 'rsync'
rsync_options = '-rtl'
import_location = os.path.join(p.padre_root,'Import')
server_id = 'id.rsa' # Path to secret key for SSH authentication
server_name = 'user@server:location' # Path to data to rsync

# labels used to help with auto-naming
dset_labels = {
    'anatomy': ['Ax_FSPGR_3D'],
    'field_map': ['Ax_GRE_TE'],
    'rest': ['fMRI_rest_run1'],
    'dti': ['DTI_2mm']
}

# files matching these masks are treated as potential datasets
archive_masks = ['*.tgz','p??','p???']
# don't try to reconstruct datasets with these labels
dset_ignore_masks = ['3Plane_Loc','Screen_Save']

# dataset groups are labeled by "PI"
pis = []

# settings for running padre_web.py
web_hostname = 'localhost'
web_port = 8080
web_server = 'tornado'
