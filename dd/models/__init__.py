from .docaligner.aligner.DocAligner import DocAligner_model

def get_model(name, n_classes=1, filters=64,version=None,in_channels=3, is_batchnorm=True, norm='batch', model_path=None, use_sigmoid=True, layers=3,img_size=512):
    model = _get_model_instance(name)
    
    model = model(batch_norm=True, pyramid_type='VGG',
                    div=1, evaluation=False,
                    consensus_network=False,
                    cyclic_consistency=True,
                    dense_connection=True,
                    decoder_inputs='corr_flow_feat',
                    refinement_at_all_levels=False,
                    refinement_at_adaptive_reso=True)
    return model


def _get_model_instance(name):
    try:
        return {'docaligner':DocAligner_model}[name]
    except:
        print('Model {} not available'.format(name))
