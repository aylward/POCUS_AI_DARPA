import itk
from itk import TubeTK as tube

import numpy as np

class ARGUS_pnb_roi_inference():
    
    def __init__(self):
        ImageF = itk.Image[itk.F, 2]
        
        self.distmap_filter = itk.DanielssonDistanceMapImageFilter[ImageF, ImageF].New()
        self.imagemath_filter = tube.ImageMath[ImageF].New()
        
        self.decision_distance = 9.0
        
    def inference(self, ar_image, ar_labels):
        artery_labels = np.where(ar_labels==1,1,0)
        artery_labels_img = itk.GetImageFromArray(artery_labels.astype(np.float32))
        spacing3d = ar_image.GetSpacing()
        spacing2d = [spacing3d[0], spacing3d[1]]
        artery_labels_img.SetSpacing(spacing2d)

        self.distmap_filter.SetInput(artery_labels_img)
        self.distmap_filter.SetUseImageSpacing(True)
        self.distmap_filter.Update()
        distmap = self.distmap_filter.GetOutput()

        self.imagemath_filter.SetInput(distmap)
        self.imagemath_filter.Threshold(0,self.decision_distance,1,0)
        artery_mask = itk.GetArrayFromImage(self.imagemath_filter.GetOutput())

        needle_labels = np.where(ar_labels==2,1,0)

        needle_mask = artery_mask * needle_labels

        needle_count = np.count_nonzero(needle_mask)
        
        needle_weight = 0
        if needle_count > 0:
            weight_array = itk.GetArrayFromImage(distmap)
            needle_weight = np.sum(needle_mask * weight_array) / needle_count
            needle_weight = ((self.decision_distance - needle_weight) / self.decision_distance)

        classification = 0
        if needle_count > 5:
            classification = 1
        prob = [needle_count, needle_weight]

        return classification, prob

