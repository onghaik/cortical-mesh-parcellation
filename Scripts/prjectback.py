def predict_segmentation(vertices, faces, output_maps, ids_maps_o, weights_maps_full_o, probs):
    """
    Calculate Lhat based on input data.

    Args:
    vertices (numpy.ndarray): Vertices.
    output_maps (list): List of output maps.
    ids_maps_o (list): List of ids maps.
    weights_maps_full_o (list): List of full weights maps.
    probs (list): List of probabilities.
    Returns:
    numpy.ndarray: Lhat array.
    """
    print('Agregating predicted labels...')
    NV = len(vertices)
    NL = 37
    P = np.zeros([NL, NV])
    # P[0, :] = 1e-6
    touched = np.zeros(NV)

    for ids_map, weights_map_full, prob in zip(ids_maps_o, weights_maps_full_o, probs):
        view = prob  # Shape is 37,800,800
        weights_map_full = weights_map_full

        vert_idx = faces[ids_map]  # Shape is 800, 800, 3

        for v in range(3):
            v_map = vert_idx[:, :, v][np.newaxis, ...]  # Shape is 1, 800, 800
            w_map = weights_map_full[:, :, v][np.newaxis, ...]
            s_map = view
            ws_map = s_map * w_map  # Shape is 37, 800, 800

            for i in range(800):
                for j in range(800):
                    v_idx = v_map[0, i, j]
                    P[:, v_idx] += ws_map[:, i, j]
                    touched[v_idx] = 1

    Lhat = np.argmax(P, axis=0)
    Lhat -= 1
    # P /= np.sum(P, axis=0)[np.newaxis, :]
    print('Labels aggregated!')

    return Lhat, P



def compute_output_maps(mesh, img_width, img_height):
    a = mesh.vertex.positions.cpu().numpy().copy()
    b = mesh.vertex.normals.cpu().numpy().copy()
    a /= np.sqrt(np.sum(a*a, axis=1))[:, np.newaxis]
    dot = np.sum(a * b, axis=1)
    
    if np.mean(dot) < 0:
        mesh.vertex.normals[:, 0] *= -1
        mesh.triangle.normals[:, 0] *= -1
        mesh.vertex.normals[:, 1] *= -1
        mesh.triangle.normals[:, 1] *= -1
        mesh.vertex.normals[:, 2] *= -1
        mesh.triangle.normals[:, 2] *= -1

    rotation_matrices = compute_rotations(view='All')
    v_n = mesh.vertex.normals
    t_n = mesh.triangle.normals
    output_maps = []
    ids_maps_o = []
    weights_maps_full_o = []
    extmats = []

    intmat = compute_intmat(img_width, img_height)
    extmat = compute_extmat(mesh)

    scene = o3d.t.geometry.RaycastingScene()
    scene.add_triangles(mesh)

    for i, rotation_matrix in enumerate(rotation_matrices): 
        extmats.append(np.matmul(extmat, rotation_matrix))

    for i in range(rotation_matrices.shape[0]): 
        mesh.vertex.normals = v_n @ np.transpose(rotation_matrices[i][:3,:3].astype(np.float32))
        mesh.triangle.normals = t_n @ np.transpose(rotation_matrices[i][:3,:3].astype(np.float32))
        rays = scene.create_rays_pinhole(intmat, extmats[i], img_width, img_height)

        cast = scene.cast_rays(rays)
        ids_map = np.array(cast['primitive_ids'].numpy(), dtype=np.int32)
        ids_maps_o.append(ids_map)
        hit_map = np.array(cast['t_hit'].numpy(), dtype=np.float32)
        weights_map = np.array(cast['primitive_uvs'].numpy(), dtype=np.float32)
        missing_weight = 1 - np.sum(weights_map, axis=2, keepdims=True)
        weights_map_full = np.concatenate((weights_map, missing_weight), axis=2)
        weights_maps_full_o.append(weights_map_full)
        label_ids = np.argmax(np.concatenate((weights_map, missing_weight), axis=2), axis=2)

        normal_map = np.array(mesh.triangle.normals[ids_map.clip(0)].numpy(), dtype=np.float32)
        normal_map[ids_maps_o[i] == -1] = [0, 0, -1]
        normal_map[:, :, -1] = -normal_map[:, :, -1].clip(-1, 0)
        normal_map = normal_map * 0.5 + 0.5

        vertex_map = np.array(mesh.triangle.indices[ids_map.clip(0)].numpy(), dtype=np.int32)
        vertex_map[ids_map == -1] = [-1]

        inverse_distance_map = 1 / hit_map
        coded_map_inv = normal_map * inverse_distance_map[:, :, None]
        output_map = (coded_map_inv - np.min(coded_map_inv)) / (np.max(coded_map_inv) - np.min(coded_map_inv))
        output_maps.append(output_map)

    return np.array(output_maps), ids_maps_o, weights_maps_full_o