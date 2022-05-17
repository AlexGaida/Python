# from maya_utils import file_utils

# reload(file_utils)

# # publish props
# file_dir = file_utils.current_file_parent(level=2)
# publish_path = file_utils.concatenate_path(file_dir, 'publish', 'v01')
# file_utils.build_directory(publish_path)

# rig_dir = file_utils.concatenate_path(file_dir, 'rig')

# # prp_floatingCamD_ctrlMocapRig_v01.ma
# files = file_utils.get_files(rig_dir, file_ext='.ma')
# file_name = ""
# for file_name in files:
#     if "ctrlMocapRig_v01" in file_name:
#         print file_name
#         break

# f_name = file_utils.split_file_name(file_name)
# f_name = f_name.replace('_ctrlMocapRig_v01', '')
# destination_file = file_utils.concatenate_path(publish_path, f_name)
# if file_utils.is_file(file_name):
#     file_utils.copy_file(file_name, destination_file)

# destination_file = file_utils.concatenate_path(file_dir, f_name)
# if file_utils.is_file(file_name):
#     file_utils.copy_file(file_name, destination_file)

# # prp_floatingCamD_mocapRig_v01.fbx
# files = file_utils.get_files(rig_dir, file_ext='.fbx')
# file_name = ""
# for file_name in files:
#     if "mocapRig_v01" in file_name:
#         print file_name
#         break

# f_name = file_utils.split_file_name(file_name)
# f_name = f_name.replace('_mocapRig_v01', '')
# destination_file = file_utils.concatenate_path(publish_path, f_name)
# if file_utils.is_file(file_name):
#     file_utils.copy_file(file_name, destination_file)

# destination_file = file_utils.concatenate_path(file_dir, f_name)
# if file_utils.is_file(file_name):
#     file_utils.copy_file(file_name, destination_file)


print(cmds.about(q=1, api=True))