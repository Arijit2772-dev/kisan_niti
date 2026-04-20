# Step 1: State-of-the-Art Models and Available Datasets

This section prepares the material requested by the supervisor: a list of state-of-the-art models used in agricultural price forecasting/cooperative selling systems, and datasets available for applying these models.

## 1. State-of-the-Art Models

| Category | Models | Role in This Research | Notes / Literature Link |
|---|---|---|---|
| Statistical time-series baselines | ARIMA, SARIMA, ARIMAX | Baseline forecasting of mandi prices | Useful as interpretable traditional models, but usually weak for nonlinear and volatile commodity prices. |
| Classical machine learning | SVR, Random Forest, XGBoost, LightGBM | Nonlinear price forecasting using lag features and external variables | Strong tabular baselines; XGBoost is practical and fast for early experiments. |
| Recurrent deep learning | RNN, LSTM, GRU, ESN | Learn temporal dependencies in commodity price series | LSTM and GRU are commonly reported as strong models for Indian agricultural commodity price prediction. |
| Hybrid forecasting models | VAR-LSTM, TCN-XGBoost, VMD-LSTM, CEEMDAN-TDNN | Combine statistical decomposition or covariates with deep learning | Useful where price series have strong seasonality, noise, and sudden spikes. |
| Modern deep forecasting models | N-BEATS, NBEATSX, Transformer, TransformerX, Temporal Fusion Transformer | Model long-range dependencies and include exogenous variables such as weather | NBEATSX and TransformerX are especially relevant because they can include weather variables. |
| Spatiotemporal graph neural networks | StemGNN, T-GCN, STGCN, DCRNN, A3T-GCN | Capture relationships between multiple mandis or commodities over time | Most relevant to the novelty of this paper because mandi prices are spatially and behaviourally connected. |
| Cooperative optimisation models | Linear Programming, Mixed Integer Linear Programming, Genetic Algorithm, Particle Swarm Optimisation | Convert forecasts into farmer-mandi-day selling schedules | Needed for the final cooperative selling decision layer. |
| Game-theoretic allocation models | Shapley Value, Modified Shapley-TOPSIS, Stackelberg Game | Fair profit/risk sharing among FPO members | Useful for ensuring cooperation remains acceptable to farmers. |
| Explainable AI models | SHAP, LIME, Counterfactual Explanations | Explain why a model recommends selling at a certain mandi/date | Important for farmer trust and FPO manager adoption. |
| Farmer advisory and delivery models | RAG, multilingual chatbot, GPT-based assistant, LLaMA-based assistant | Deliver recommendations in Hindi/Punjabi/English through WhatsApp or dashboard | Relevant for the advisory layer, but not the first experiment. |

## 2. Available Datasets

| Dataset / Source | Data Type | Main Fields | Why It Is Useful | Suitability |
|---|---|---|---|---|
| AGMARKNET / data.gov.in mandi prices | Indian mandi-level daily price data | State, district, market, commodity, variety, min price, max price, modal price, arrival date | Most important dataset for this paper because the research problem is Indian mandi price forecasting and selling optimisation | Very high |
| NASA POWER | Weather and agro-climatic data | Temperature, rainfall, humidity, wind speed, solar radiation, date, location | Can be joined with mandi price data to test weather-augmented models such as NBEATSX and TransformerX | High |
| e-NAM market information | Indian agricultural market data | Commodity, market, price/arrival details where available | Useful as supporting market data, though access and structure may be less direct than AGMARKNET | Medium |
| World Bank Pink Sheet | Global monthly commodity prices | Monthly international prices for agricultural and non-agricultural commodities | Useful for macro-level reference or global comparison, but not mandi-level prediction | Medium |
| OpenStreetMap / OSRM | Location and route data | Mandi coordinates, road distance, travel time | Useful for transport-cost-aware mandi selection and graph construction | High for optimisation stage |
| IoT grain storage sensor data | Storage condition data | Temperature, humidity, gas concentration, grain weight, timestamp | Useful for modelling storage urgency, but public datasets are limited and often prototype-specific | Medium |
| Kisan Call Center / farmer advisory data | Farmer query-response data | Crop, region, query, expert response | Useful for advisory chatbot layer, not price forecasting | Medium |

## 3. Dataset Selected for First Experiment

The recommended dataset for the first experiment is **AGMARKNET mandi price data**, because:

1. It is the most directly aligned with the research problem.
2. It contains daily mandi-level prices for many commodities and markets.
3. It has already been used in recent agricultural price forecasting literature.
4. It supports comparison between classical, machine learning, deep learning, and graph-based models.

## 4. Recommended First Experimental Scope

To keep the first experiment manageable, start with one commodity and multiple mandis.

Recommended option:

| Item | Choice |
|---|---|
| Commodity | Paddy or Wheat, because the paper focuses on grain storage and FPO selling |
| Alternative commodity | Onion or Tomato, because price volatility is higher and model differences become more visible |
| Target variable | Modal price |
| Forecast horizon | 7-day ahead forecasting |
| Train-test split | 80% training, 20% testing, chronological split |
| Metrics | RMSE, MAE, MAPE or sMAPE |

## 5. Models to Apply First

Start with these models before moving to graph neural networks:

| Priority | Model | Reason |
|---|---|---|
| 1 | Naive baseline | Checks whether advanced models are actually useful. |
| 2 | ARIMA | Traditional statistical baseline expected in time-series papers. |
| 3 | XGBoost | Strong machine learning baseline using lag features. |
| 4 | LSTM | Standard deep learning model for sequential forecasting. |
| 5 | GRU | Often performs similarly to or better than LSTM with lower complexity. |
| 6 | T-GCN / StemGNN / A3T-GCN | Add after the basic models work, because graph models need multi-mandi graph construction. |

## 6. Expected Result Table Format

After running the models, results should be reported in this format:

| Model | RMSE | MAE | MAPE / sMAPE | Interpretation |
|---|---:|---:|---:|---|
| Naive baseline | To be computed | To be computed | To be computed | Baseline using previous value. |
| ARIMA | To be computed | To be computed | To be computed | Traditional time-series model. |
| XGBoost | To be computed | To be computed | To be computed | Machine learning model using lag features. |
| LSTM | To be computed | To be computed | To be computed | Deep learning sequence model. |
| GRU | To be computed | To be computed | To be computed | Deep learning sequence model with fewer parameters than LSTM. |
| Graph model | To be computed | To be computed | To be computed | Captures spatial/market relationships between mandis. |

## 7. How This Connects Back to the Paper

This experimental section will strengthen the review paper by showing that the proposed direction is not only theoretical. The paper can argue that:

1. Traditional models provide useful baselines but struggle with nonlinear price behaviour.
2. Deep learning models such as LSTM and GRU are stronger for temporal mandi price forecasting.
3. Weather-augmented models can improve forecasting where exogenous variables are important.
4. Graph neural networks are the most relevant next step because FPO selling decisions depend on relationships between multiple mandis, not isolated price series.
5. Forecasting results can later be connected to the cooperative selling optimiser.
