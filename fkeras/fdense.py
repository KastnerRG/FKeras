from qkeras import QDense
from keras import backend
import fkeras as fk
from fkeras.utils import gen_lbi_region_at_layer_level, quantize_and_bitflip, FKERAS_quantize_and_bitflip
import tensorflow.compat.v2 as tf

assert tf.executing_eagerly(), "QKeras requires TF with eager execution mode on"

class FQDense(QDense):
    """
    Implements a faulty QDense layer

    Parameters:
    * ber (float): Bit Error Rate, or how often you want a fault to occur
    * bit_loc (list of tuples): Target ranges for the bit errors, e.g., (0, 3) targets bits at index 0 through 3, where 0 is the LSB. 

    Please refer to the documentation of QDense in QKeras for the other
    parameters.
    """

    def __init__(self, units, ber=0.0, bit_loc=0, **kwargs):
        self.ber = ber
        self.bit_loc = bit_loc

        super(FQDense, self).__init__(units=units, **kwargs)

    # def call(self, inputs):
        # original_kernel = self.kernel

        # self.kernel = faulty_kernel

        # super_outputs = super().call(inputs)

        # self.kernel = original_kernel


        # super_outputs = super().call(inputs)
        # # TODO: Induce bitflips at ber at the indicated bit_loc
        # pass
        # #backend.learning_phase() (0 is Test | 1 is Train)
        # if backend.learning_phase() == 0:
            
        # return super_outputs

    def call(self, inputs):
        # TODO: Implement bit error rate
        # if inducing error, get faulty_qkernel
        # else: do 
            # Original qkeras
            # if self.kernel_quantizer:
            #     quantized_kernel = self.kernel_quantizer_internal(self.kernel)
            # else:
            #     quantized_kernel = self.kernel
        # faulty_qkernel = quantize_and_bitflip(
        #     self.kernel, 
        #     self.kernel_quantizer_internal,
        #     self.bit_loc,
        #     self.ber
        # )

        #TODO: Update the following code block with function call that
        ###### returns the same lbi region
        quant_config = self.kernel_quantizer_internal.get_config()
        faulty_layer_bit_region = gen_lbi_region_at_layer_level(
            self.kernel,
            quant_config['bits'],
            self.ber
        )[0]
        faulty_qkernel = quantize_and_bitflip(
            self.kernel, 
            self.kernel_quantizer_internal, 
            [(faulty_layer_bit_region.start_lbi, faulty_layer_bit_region.end_lbi)], 
            [faulty_layer_bit_region.ber]
        )
        # print(f"[fkeras - Dense.call()] {tf.executing_eagerly()}")
        # faulty_qkernel = FKERAS_quantize_and_bitflip( 
        #     self.kernel_quantizer_internal, 
        #     [(faulty_layer_bit_region.start_lbi, faulty_layer_bit_region.end_lbi)], 
        #     [faulty_layer_bit_region.ber]
        # )(self.kernel)
        output = tf.keras.backend.dot(inputs, faulty_qkernel)
        if self.use_bias:
            if self.bias_quantizer:
                quantized_bias = self.bias_quantizer_internal(self.bias)
            else:
                quantized_bias = self.bias
            output = tf.keras.backend.bias_add(output, quantized_bias,
                                            data_format="channels_last")
        if self.activation is not None:
            output = self.activation(output)
        return output



