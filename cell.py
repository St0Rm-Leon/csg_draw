from shapes import SignedShape 
import numpy as np 

class Cell:
    def __init__(self, geom_list):
        self.geom_sign_list, self.geom_id_list = self.decouple(geom_list)

    def decouple(self, geom_list):
        geom_sign_list = []
        geom_id_list = []

        for item in geom_list:
            if isinstance(item, SignedShape):
                geom_sign_list.append(item.sign)
                geom_id_list.append(item.shape)
            else:
                geom_sign_list.append(1)
                geom_id_list.append(item)

        return geom_sign_list, geom_id_list

    def print_info(self):
        print(self.geom_sign_list)
        print(self.geom_id_list)

    def is_inside_cell(self, px0, py0, pz0):
        if isinstance(px0, np.ndarray):
            result = np.ones_like(px0, dtype=bool)
            for sign, shape in zip(self.geom_sign_list,
                                   self.geom_id_list):
                is_positive = shape.is_positive(px0,py0,pz0)
                result = result & (is_positive if sign == 1 else ~is_positive)
            return result
        else:
            for sign, shape in zip(self.geom_sign_list,
                                   self.geom_id_list):
                is_positive = shape.is_positive(px0, py0, pz0) 
                if sign == -1:
                    is_positive = not shape.is_positive(px0, py0, pz0)
                if not is_positive:
                    return False 

            return True 
