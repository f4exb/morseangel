import torch
import torch.nn as nn
import numpy as np


class MorseBatchedLSTMStack(nn.Module):
    """
    LSTM stack with dataset input
    """
    def __init__(self, device, nb_lstm_layers=2, input_size=1, hidden_layer_size=8, output_size=6, dropout=0.2):
        super().__init__()
        self.device = device # This is the only way to get things work properly with device
        self.nb_lstm_layers = nb_lstm_layers
        self.input_size = input_size
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_layer_size, num_layers=self.nb_lstm_layers, dropout=dropout)
        self.linear = nn.Linear(hidden_layer_size, output_size)
        self.hidden_cell = (torch.zeros(self.nb_lstm_layers, 1, self.hidden_layer_size).to(self.device),
                            torch.zeros(self.nb_lstm_layers, 1, self.hidden_layer_size).to(self.device))
        self.use_minmax = False

    def _minmax(self, x):
        x -= x.min(0)[0]
        x /= x.max(0)[0]

    def _hardmax(self, x):
        x /= x.sum()

    def _sqmax(self, x):
        x = x**2
        x /= x.sum()

    def forward(self, input_seq):
        #print(len(input_seq), input_seq.shape, input_seq.view(-1, 1, 1).shape)
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(-1, 1, self.input_size), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        if self.use_minmax:
            self._minmax(predictions[-1])
        return predictions[-1]

    def zero_hidden_cell(self):
        self.hidden_cell = (
            torch.zeros(self.nb_lstm_layers, 1, self.hidden_layer_size).to(device),
            torch.zeros(self.nb_lstm_layers, 1, self.hidden_layer_size).to(device)
        )

class Predictions:
    def __init__(self):
        self.tbuffer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Torch using {self.device}")
        self.max_ele = 5 # Number of Morse elements considered
        self.look_back = 208 # Constant coming from model training
        self.model = MorseBatchedLSTMStack(self.device, nb_lstm_layers=2, hidden_layer_size=60, output_size=self.max_ele+2, dropout=0.1).to(self.device)
        self.model.use_minmax = True
        self.lp_len = 3
        self.lp_win = np.ones(self.lp_len) / self.lp_len
        self.lp = True # post process predictions through moving average low pass filtering

    @staticmethod
    def pytorch_rolling_window(x, window_size, step_size=1):
        # unfold dimension to make our rolling window
        return x.unfold(0,window_size,step_size)

    def load_model(self, filename):
        self.model.load_state_dict(torch.load(filename, map_location=self.device))
        self.model.eval()

    def new_data(self, data):
        """ Takes the latest portion of the signal envelope as a numpy array,
            make predictions using the model and interpret results to produce decoded text.
        """
        if self.tbuffer is None:
            self.tbuffer = torch.FloatTensor(data).to(self.device)
        else:
            self.tbuffer = torch.cat((self.tbuffer, torch.FloatTensor(data).to(self.device)))
        if len(self.tbuffer) > self.look_back:
            l = len(self.tbuffer) - self.look_back + 1
            self.cbuffer = self.tbuffer[-l:].cpu()
            X_tests = self.pytorch_rolling_window(self.tbuffer, self.look_back, 1)
            self.tbuffer = X_tests[-1][1:]
            p_preds = torch.empty(1, self.max_ele+2).to(self.device)
            for X_test in X_tests:
                with torch.no_grad():
                    y_pred = self.model(X_test)
                    p_preds = torch.cat([p_preds, y_pred.reshape(1, self.max_ele+2)])
            p_preds = p_preds[1:] # drop first garbage sample
            p_preds_t = torch.transpose(p_preds, 0, 1).cpu()
            if self.lp:
                p_preds_t = np.apply_along_axis(lambda m: np.convolve(m, self.lp_win, mode='full'), axis=1, arr=p_preds_t)
                self.p_preds_t = p_preds_t[:,:-self.lp_len+1]
            else:
                self.p_preds_t = p_preds_t
        else:
            self.p_preds_t = None
            self.cbuffer = None
