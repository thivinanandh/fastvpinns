"""
This function is implemntation of our efficient tensor-based loss calculation for cd2d equation
Author: Thivin Anandh D
Date: 21-Sep-2023
History: Initial implementation
Refer: https://arxiv.org/abs/2404.12063
"""

import tensorflow as tf


# PDE loss function for the cd2d problem
@tf.function
def pde_loss_cd2d(
    test_shape_val_mat,
    test_grad_x_mat,
    test_grad_y_mat,
    pred_nn,
    pred_grad_x_nn,
    pred_grad_y_nn,
    forcing_function,
    bilinear_params,
):  # pragma: no cover
    """
    Calculates and returns the loss for the CD2D problem

    :param test_shape_val_mat: The test shape value matrix.
    :type test_shape_val_mat: tf.Tensor
    :param test_grad_x_mat: The x-gradient of the test matrix.
    :type test_grad_x_mat: tf.Tensor
    :param test_grad_y_mat: The y-gradient of the test matrix.
    :type test_grad_y_mat: tf.Tensor
    :param pred_nn: The predicted neural network output.
    :type pred_nn: tf.Tensor
    :param pred_grad_x_nn: The x-gradient of the predicted neural network output.
    :type pred_grad_x_nn: tf.Tensor
    :param pred_grad_y_nn: The y-gradient of the predicted neural network output.
    :type pred_grad_y_nn: tf.Tensor
    :param forcing_function: The forcing function used in the PDE.
    :type forcing_function: function
    :param bilinear_params: The parameters for the bilinear form.
    :type bilinear_params: list


    :return: The calculated loss.
    :rtype: tf.Tensor
    """

    # Loss Function : ∫du/dx. dv/dx  +  ∫du/dy. dv/dy - ∫f.v

    # ∫du/dx. dv/dx dΩ
    pde_diffusion_x = tf.transpose(tf.linalg.matvec(test_grad_x_mat, pred_grad_x_nn))

    # ∫du/dy. dv/dy dΩ
    pde_diffusion_y = tf.transpose(tf.linalg.matvec(test_grad_y_mat, pred_grad_y_nn))

    # eps * ∫ (du/dx. dv/dx + du/dy. dv/dy) dΩ
    pde_diffusion = bilinear_params["eps"] * (pde_diffusion_x + pde_diffusion_y)

    # ∫du/dx. v dΩ
    conv_x = tf.transpose(tf.linalg.matvec(test_shape_val_mat, pred_grad_x_nn))

    # # ∫du/dy. v dΩ
    conv_y = tf.transpose(tf.linalg.matvec(test_shape_val_mat, pred_grad_y_nn))

    # # b(x) * ∫du/dx. v dΩ + b(y) * ∫du/dy. v dΩ
    conv = bilinear_params["b_x"] * conv_x + bilinear_params["b_y"] * conv_y

    # reaction term
    # ∫c.u.v dΩ
    reaction = bilinear_params["c"] * tf.transpose(tf.linalg.matvec(test_shape_val_mat, pred_nn))

    residual_matrix = (pde_diffusion + conv + reaction) - forcing_function

    # Perform Reduce mean along the axis 0
    residual_cells = tf.reduce_mean(tf.square(residual_matrix), axis=0)

    return residual_cells
