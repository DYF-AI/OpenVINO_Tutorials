"""
Copyright (c) 2018-2020 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from ..config import PathField, StringField, ConfigError
from ..representation import ImageProcessingAnnotation
from ..representation.image_processing import GTLoader
from ..utils import check_file_existence
from .format_converter import BaseFormatConverter, ConverterReturn

LOADERS_MAPPING = {
    'opencv': GTLoader.OPENCV,
    'pillow': GTLoader.PILLOW,
    'dicom': GTLoader.DICOM
}


class ImageProcessingConverter(BaseFormatConverter):
    __provider__ = 'image_processing'
    annotation_types = (ImageProcessingAnnotation, )

    @classmethod
    def parameters(cls):
        configuration_parameters = super().parameters()
        configuration_parameters.update({
            'data_dir': PathField(
                is_directory=True, description="Path to folder where input and target images are located."
            ),
            'input_suffix': StringField(
                optional=True, default="in", description="input file name's suffix."
            ),
            'target_suffix': StringField(
                optional=True, default="out", description="gt file name's suffix."
            ),
            'annotation_loader': StringField(
                optional=True, choices=LOADERS_MAPPING.keys(), default='pillow',
                description="Which library will be used for ground truth image reading. "
                            "Supported: {}".format(', '.join(LOADERS_MAPPING.keys()))
            )
        })

        return configuration_parameters

    def configure(self):
        self.data_dir = self.get_value_from_config('data_dir')
        self.in_suffix = self.get_value_from_config('input_suffix')
        self.out_suffix = self.get_value_from_config('target_suffix')
        self.annotation_loader = LOADERS_MAPPING.get(self.get_value_from_config('annotation_loader'))
        if not self.annotation_loader:
            raise ConfigError('provided not existing loader')

    def convert(self, check_content=False, progress_callback=None, progress_interval=100, **kwargs):
        content_errors = [] if check_content else None
        file_list_in = []
        for file_in_dir in self.data_dir.iterdir():
            if self.in_suffix in file_in_dir.parts[-1]:
                file_list_in.append(file_in_dir)

        annotation = []
        num_iterations = len(file_list_in)
        for in_id, in_file in enumerate(file_list_in):
            in_file_name = in_file.parts[-1]
            gt_file_name = self.out_suffix.join(in_file_name.split(self.in_suffix))
            if check_content:
                if not check_file_existence(self.data_dir / gt_file_name):
                    content_errors.append('{}: does not exist'.format(self.data_dir / gt_file_name))

            identifier = in_file_name
            annotation.append(ImageProcessingAnnotation(identifier, gt_file_name, gt_loader=self.annotation_loader))
            if progress_callback is not None and in_id % progress_interval == 0:
                progress_callback(in_id / num_iterations * 100)

        return ConverterReturn(annotation, None, content_errors)
