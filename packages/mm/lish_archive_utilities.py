import pathlib
import os
import typing

#------------------------------------------------------------------------------    
# Helper function to get paths to project folders
#------------------------------------------------------------------------------ 
def build_archive_path_dict():
     current_path = pathlib.Path(os.getcwd())

     archive_root = build_archive_root_path(current_path)


     if archive_root is not pathlib.Path():          
          archive_datasets_root = archive_root.joinpath('datasets')
          archive_projects_root = archive_root.joinpath('projects')

          project_root = build_project_root_path(current_path, archive_projects_root)
          dataset_root = build_project_root_path(current_path, archive_datasets_root)

          original_root = dataset_root.joinpath('original')
          processed_root = dataset_root.joinpath('processed')

          input_root = project_root.joinpath('input')
          output_root = project_root.joinpath('output')
     else:
          archive_root          = pathlib.Path()
          archive_datasets_root = pathlib.Path()
          archive_projects_root = pathlib.Path()
          project_root          = pathlib.Path()

     return {'root':archive_root,'datasets':archive_datasets_root,'projects':archive_projects_root,
             'this_project':project_root, 'this_input':input_root, 'this_output':output_root,
             'this_dataset':dataset_root, 'this_original': original_root, 'this_processed':processed_root}

#------------------------------------------------------------------------------ 
def build_archive_root_path(in_path):
     
     parent_stem_list = [x.stem for x in in_path.parents]

     if 'archive' in  parent_stem_list:
          idx = parent_stem_list.index('archive')          
          archive_root = in_path.parents[idx]
     else:
          archive_root = pathlib.Path()

     return archive_root

#------------------------------------------------------------------------------ 
def build_project_root_path(in_path, archive_projects_root):
     
     archive_projects_root_child_list = [x for x in archive_projects_root.iterdir()]
     archive_projects_root_child_stem_list = [x.stem for x in archive_projects_root.iterdir()]

     archive_projects_root_dict = dict(zip(archive_projects_root_child_stem_list, archive_projects_root_child_list))
     in_path_parent_stem_set    = set([x.stem for x in in_path.parents])

     shared_stem = in_path_parent_stem_set.intersection(archive_projects_root_dict.keys())

     if len(shared_stem) == 1:
          project_root = archive_projects_root_dict[shared_stem.pop()]
     else:
          project_root = pathlib.Path()

     return project_root

#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------    
# Run to test the returned paths
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
if __name__ == '__main__':
     current_path = pathlib.Path(os.path.dirname(os.getcwd()))

     archive_path_dict = build_archive_path_dict()

     print('Current Path:')
     print(current_path)

     print('Archive Root:')
     print(archive_path_dict['root'])

     print('Archive Projects Root:')
     print(archive_path_dict['projects'])

     print('Archive Datasets Root:')
     print(archive_path_dict['datasets'])

     print('Project Root:')
     print(archive_path_dict['this_project'])

     print('Project Input Root:')
     print(archive_path_dict['this_input'])

     print('Project Output Root:')
     print(archive_path_dict['this_output'])

     print('Dataset Root:')
     print(archive_path_dict['this_dataset'])

     print('Original Root:')
     print(archive_path_dict['this_original'])

     print('Processed Root:')
     print(archive_path_dict['this_processed'])