import cv2
import sys
import numpy as np


def compute_error(point1, point2, h):
    # Convert to homogeneous coordinates
    point1H = np.array([point1[0], point1[1], 1])
    # Convert to normal coordinates
    point1predicted = np.dot(h, point1H.transpose())
    point1predictednormal = point1predicted / point1predicted[2]
    error = np.linalg.norm(
        point2 - point1predictednormal[0:2])  # Calculate error

    return error


def compute_homography(x1, y1, x2, y2, x3, y3, x4, y4, xp1, yp1, xp2, yp2, xp3, yp3, xp4, yp4):
    A = np.array([[-1 * x1, -1 * y1, -1, 0, 0, 0, x1 * xp1, y1 * xp1, xp1],
                  [0, 0, 0, -1 * x1, -1 * y1, -1, x1 * yp1, y1 * yp1, yp1],
                  [-1 * x2, -1 * y2, -1, 0, 0, 0, x2 * xp2, y2 * xp2, xp2],
                  [0, 0, 0, -1 * x2, -1 * y2, -1, x2 * yp2, y2 * yp2, yp2],
                  [-1 * x3, -1 * y3, -1, 0, 0, 0, x3 * xp3, y3 * xp3, xp3],
                  [0, 0, 0, -1 * x3, -1 * y3, -1, x3 * yp3, y3 * yp3, yp3],
                  [-1 * x4, -1 * y4, -1, 0, 0, 0, x4 * xp4, y4 * xp4, xp4],
                  [0, 0, 0, -1 * x4, -1 * y4, -1, x4 * yp4, y4 * yp4, yp4]
                  ])
    [U, S, V] = np.linalg.svd(A)
    H = V[-1:]
    H = np.reshape(H, (3, 3))

    return H


def ex_find_homography_ransac(list_pairs_matched_keypoints, threshold_ratio_inliers=0.85, threshold_reprojtion_error=3, max_num_trial=1000):
    '''
    Apply RANSAC algorithm to find a homography transformation matrix that align 2 sets of feature points, transform the first set of feature point to the second (e.g. warp image 1 to image 2)
    :param list_pairs_matched_keypoints: has the format as a list of pairs of matched points: [[[p1x,p1y],[p2x,p2y]],....]
    :param threshold_ratio_inliers: threshold on the ratio of inliers over the total number of samples, accept the estimated homography if ratio is higher than the threshold
    :param threshold_reprojtion_error: threshold of reprojection error (measured as euclidean distance, in pixels) to determine whether a sample is inlier or outlier
    :param max_num_trial: the maximum number of trials to do take sample and do testing to find the best homography matrix
    :return best_H: the best found homography matrix
    '''
    best_H = None
    # print(list_pairs_matched_keypoints)
    # to be completed ...
    for x in range(max_num_trial):  # Select seed group of matches
        first = list_pairs_matched_keypoints[np.random.randint(
            0, len(list_pairs_matched_keypoints))]
        second = list_pairs_matched_keypoints[np.random.randint(
            0, len(list_pairs_matched_keypoints))]
        third = list_pairs_matched_keypoints[np.random.randint(
            0, len(list_pairs_matched_keypoints))]
        fourth = list_pairs_matched_keypoints[np.random.randint(
            0, len(list_pairs_matched_keypoints))]

        h = compute_homography(first[0][0], first[0][1], second[0][0], second[0][1], third[0][0], third[0][1], fourth[0][0], fourth[0][1],
                               first[1][0], first[1][1], second[1][0], second[1][1], third[1][0], third[1][1], fourth[1][0], fourth[1][1])
        # h = compute_homography(first[0][1], first[0][0], second[0][1], second[0][0], third[0][1], third[0][0], fourth[0][1], fourth[0][0],
        # first[1][1], first[1][0], second[1][1], second[1][0], third[1][1], third[1][0], fourth[1][1], fourth[1][0])
        # h = compute_homography(first[1][0], first[1][1], second[1][0], second[1][1], third[1][0], third[1][1], fourth[1][0], fourth[1][1],
        # first[0][0], first[0][1], second[0][0], second[0][1], third[0][0], third[0][1], fourth[0][0], fourth[0][1])

        inliers = 0
        for i in range(len(list_pairs_matched_keypoints)):
            # Passes in pair of matched points
            error = compute_error(
                list_pairs_matched_keypoints[i][0], list_pairs_matched_keypoints[i][1], h)
            if error < threshold_reprojtion_error:
                inliers += 1

        if inliers / len(list_pairs_matched_keypoints) > threshold_ratio_inliers:
            best_H = h
            break

    return best_H


def ex_extract_and_match_feature(img_1, img_2, ratio_robustness=0.7):
    '''
    1/ extract SIFT feature from image 1 and image 2,
    2/ use a bruteforce search to find pairs of matched features: for each feature point in img_1, find its best matched feature point in img_2
    3/ apply ratio test to select the set of robust matched points
    :param img_1: input image 1
    :param img_2: input image 2
    :param ratio_robustness: ratio for the robustness test
    :return list_pairs_matched_keypoints: has the format as list of pairs of matched points: [[[p1x,p1y],[p2x,p2y]]]
    '''
    # ==============================
    # ===== 1/ extract features from input image 1 and image 2
    # ==============================

    sift = cv2.SIFT_create()
    gray_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY)
    gray_2 = cv2.cvtColor(img_2, cv2.COLOR_BGR2GRAY)
    kp_1, des_1 = sift.detectAndCompute(gray_1, None)
    kp_2, des_2 = sift.detectAndCompute(gray_2, None)

    # ==============================
    # ===== 2/ use bruteforce search to find a list of pairs of matched feature points
    # ==============================
    list_pairs_matched_keypoints = []

    # to be completed ....
    for a in range(len(kp_1)):
        candidates = []
        for b in range(len(kp_2)):
            dist = np.linalg.norm(des_1[a] - des_2[b])
            candidates.append((dist, b))
        candidates.sort()
        if (candidates[0][0] / candidates[1][0]) < ratio_robustness:
            list_pairs_matched_keypoints.append(
                [[kp_1[a].pt[0], kp_1[a].pt[1]], [kp_2[candidates[0][1]].pt[0], kp_2[candidates[0][1]].pt[1]]])

    return list_pairs_matched_keypoints


def ex_warp_blend_crop_image(img_1, H_1, img_2):
    '''
    1/ warp image img_1 using the homography H_1 to align it with image img_2 (using backward warping and bilinear resampling)
    2/ stitch image img_1 to image img_2 and apply average blending to blend the 2 images into a single panorama image
    3/ find the best bounding box for the resulting stitched image
    :param img_1:
    :param H_1:
    :param img_2:
    :return img_panorama: resulting panorama image
    '''
    img_panorama = None
    # =====  use a backward warping algorithm to warp the source
    # 1/ to do so, we first create the inverse transform; 2/ use bilinear interpolation for resampling
    # to be completed ...
    h, w, d = img_2.shape
    print(H_1)
    H_1 = np.linalg.inv(H_1)  # inverse transform of H_1
    warp = cv2.warpPerspective(
        img_2, H_1, (img_2.shape[1]*2, img_2.shape[0]*2))

    #h *= 2
    #w *= 2
    #size = (w, h)
    #warp = cv2.warpPerspective(img_2, H_1, size)

    #
    # ===== blend images: average blending
    # to be completed ...
    # ===== find the best bounding box for the resulting stitched image so that it will contain all pixels from 2 original images
    # to be completed ...

    #img_panorama = np.zeros([h, w, 3])
    # for i in range(h):
    #    for j in range(w):
    #        if i < img_1.shape[0] and j < img_1.shape[1]:
    #            if warp[i, j].any():
    #                img_panorama[i, j] = np.clip(
    #                    0.5 * img_1[i, j] + 0.5 * warp[i, j], 0, 255)
    #            else:
    #                img_panorama[i, j] = img_1[i, j]
    #        else:
    #            img_panorama[i, j] = warp[i, j]

    warp[0:img_2.shape[0], 0:img_2.shape[1]] = img_1
    rows, cols = np.where(warp[:, :, 0] != 0)
    img_panorama = warp[0:max(rows) + 1, 0:max(cols) + 1, :]

    return img_panorama


def stitch_images(img_1, img_2):
    '''
    :param img_1: input image 1. We warp this image to align and stich it to the image 2
    :param img_2: is the reference image. We will not warp this image
    :return img_panorama: the resulting stiched image
    '''
    print('==============================')
    print('===== stitch two images to generate one panorama image')
    print('==============================')

    # ===== extract and match features from image 1 and image 2
    list_pairs_matched_keypoints = ex_extract_and_match_feature(
        img_1=img_1, img_2=img_2, ratio_robustness=0.7)

    # ===== use RANSAC algorithm to find homography to warp image 1 to align it to image 2
    H_1 = ex_find_homography_ransac(
        list_pairs_matched_keypoints, threshold_ratio_inliers=0.85, threshold_reprojtion_error=3, max_num_trial=1000)

    # ===== warp image 1, blend it with image 2 using average blending to produce the resulting panorama image
    img_panorama = ex_warp_blend_crop_image(img_1=img_1, H_1=H_1, img_2=img_2)
    #img_panorama = ex_warp_blend_crop_image(img_2=img_2, H_1=H_1, img_1=img_1)

    return img_panorama


if __name__ == "__main__":
    print('==================================================')
    print('PSU CS 410/510, Winter 2022, HW2: image stitching')
    print('==================================================')

    path_file_image_1 = sys.argv[1]
    path_file_image_2 = sys.argv[2]
    path_file_image_result = sys.argv[3]

    # ===== read 2 input images
    img_1 = cv2.imread(path_file_image_1)
    img_2 = cv2.imread(path_file_image_2)

    # ===== create a panorama image by stitch image 1 to image 2
    img_panorama = stitch_images(img_1=img_1, img_2=img_2)

    # ===== save panorama image
    cv2.imwrite(filename=path_file_image_result, img=(
        img_panorama).clip(0.0, 255.0).astype(np.uint8))
