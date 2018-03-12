from genut.data.load_data import *
from genut.util.argparser import ArgParser
from genut.models.seq2seq import Seq2seq
from genut.models.lm import RNNLM
# from genut.models.seq2seq_vae import
from genut.data.load_data import load_prev_state

from genut.util.eval import Tester
from genut.util.train_lm import LMTrainer

if __name__ == "__main__":
    torch.backends.cudnn.enabled = False

    ap = ArgParser()

    opt = ap.parser.parse_args()
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

    # Register for logger
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    if opt.dbg is not True:
        fileHandler = logging.FileHandler("logger.log")
        rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    rootLogger.addHandler(consoleHandler)

    logging.info('Go!')

    if opt.use_cuda and not torch.cuda.is_available():
        logging.error('GPU NOT avail.')
    elif not torch.cuda.is_available():
        logging.warning('GPU NOT avail.')

    opt, data_patch = load_dataset(opt)

    logging.info(opt)

    pretrain_embedding = load_pretrain_word_embedding(opt)

    # model = Seq2seq(opt, pretrain_embedding)
    model = RNNLM(opt, pretrain_embedding)

    if opt.use_cuda:
        model = model.cuda()

    if opt.load_dir is not None and opt.load_file is not None:
        model.enc = load_prev_state(opt.load_dir + '/' + opt.load_file + '_enc', model.enc)
        model.dec = load_prev_state(opt.load_dir + '/' + opt.load_file + '_dec', model.dec)
        model.emb = load_prev_state(opt.load_dir + '/' + opt.load_file + '_emb', model.emb)
        # try:
        #     model.emb = load_prev_state(opt.load_dir + '/' + opt.load_file + '_emb', model.emb)
        #
        # except TypeError:
        #     print("Trying another method")
        #     model.emb = util.load_prev_model(opt.load_dir + '/' + opt.load_file + '_emb', model.emb)
        #
        # try:
        #     model.feat = util.load_prev_model(opt.load_dir + '/' + opt.load_file + '_feat', model.feat)
        # except IOError:
        #     print('IOError')

    print("Model Initialized.")
    if opt.mode == TEST_FLAG:
        model.eval()
        # TODO
        os.chdir('/home/jcxu/ut-seq2seq/pythonrouge')
        s2s_test = Tester(opt, model,
                                     data=data_patch, write_file='_'.join([str(opt.max_len_enc), str(opt.max_len_dec),
                                                                         str(opt.min_len_dec), opt.load_file, opt.name,
                                                                         str(opt.beam_size), str(opt.avoid), 'result']))

        s2s_test.test_iter_non_batch()

    elif opt.mode == TRAIN_FLAG:
        model.train()
        s2s_train = LMTrainer(opt, model, data_patch)
        try:
            s2s_train.train_iters()
        except KeyboardInterrupt:
            logging.info("Training Interrupted.")
    else:
        raise RuntimeError
