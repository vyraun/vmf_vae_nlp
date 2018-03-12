import torch.nn as nn

from genut.modules.dec.decoder_srnn import SimpleRNNDecoder
from genut.modules.embedding import SingleEmbeddings
from genut.modules.enc.rnn_enc import RNNEncoder


class RNNLM(nn.Module):
    def __init__(self, opt, pretrain=None):
        super(RNNLM, self).__init__()
        self.opt = opt

        embeds = SingleEmbeddings(opt, pretrain)
        self.emb = embeds

        if self.opt.enc == 'lstm':
            enc = RNNEncoder(opt, opt.inp_dim, opt.hid_dim, rnn_type=opt.enc.lower())
        else:
            raise NotImplementedError
        self.enc = enc

        rnn_dec = SimpleRNNDecoder(opt, rnn_type='lstm', input_size=opt.inp_dim,
                                   hidden_size=opt.hid_dim, emb=self.emb)

        self.dec = rnn_dec

    def forward(self, inp_var, inp_msk, tgt_var=None, tgt_msk=None, aux=None):

        emb = self.emb.forward(inp_var)
        # Output: Combined Word Embedding

        # Input: Combined Word Embedding  seq,batch,dim
        h_t = self.enc.forward(emb, inp_msk)
        # Output: Encoded H and h[-1]. seq,batch,dim and batch,dim

        decoder_outputs_prob, decoder_outputs = self.dec.forward(
            h_t,
            tgt_var, tgt_msk,
            aux)

        # context batch seq_len, hidden_size * num_directions )
        # hidden num_layers, seq , num_directions x hidden_size)
        return decoder_outputs_prob, decoder_outputs
