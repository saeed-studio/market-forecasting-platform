# Collector Service

## Responsibility

Collect and validate realtime market data streams from external exchanges.

## Inputs

* Binance WebSocket streams
* REST API snapshots
* OHLCV data
* Trades stream
* Funding rate data
* Open interest data

## Outputs

* normalized market events
* validated realtime streams
* parquet raw datasets
* ingestion logs

## Owns

* websocket lifecycle
* reconnect logic
* stream validation
* timestamp normalization
* raw event persistence

## Does NOT Own

* feature engineering
* ML inference
* dashboard logic
* prediction generation

## Failure Modes

* websocket disconnects
* malformed payloads
* duplicate events
* missing intervals
* rate limiting
* exchange downtime

# Feature Engine

## Responsibility

Transform raw market streams into structured numerical features for ML consumption.

## Inputs

* raw market events
* OHLCV data
* trades stream
* funding rate data
* open interest data

## Outputs

* feature vectors
* engineered market state representations
* volatility features
* order flow metrics
* derivatives metrics

## Owns

* rolling window calculations
* feature normalization
* market microstructure calculations
* volatility estimation
* statistical feature extraction

## Does NOT Own

* websocket management
* model training
* inference serving
* dashboard rendering

## Failure Modes

* NaN propagation
* feature drift
* invalid rolling windows
* timestamp misalignment
* missing market intervals

# ML Pipeline

## Responsibility

Train, evaluate, and version forecasting models using temporally-valid financial datasets.

## Inputs

* feature vectors
* labeled datasets
* training configurations
* preprocessing settings

## Outputs

* trained model artifacts
* evaluation metrics
* prediction interfaces
* experiment logs
* serialized preprocessors

## Owns

* dataset splitting
* preprocessing
* model training
* model evaluation
* experiment tracking
* artifact versioning

## Does NOT Own

* realtime data collection
* websocket connections
* API serving
* frontend visualization

## Failure Modes

* overfitting
* data leakage
* unstable validation metrics
* training crashes
* invalid feature distributions
* artifact corruption

# Prediction Service

## Responsibility

Run realtime inference using trained forecasting models and expose probabilistic predictions.

## Inputs

* latest feature vectors
* trained model artifacts
* preprocessing objects

## Outputs

* expected returns
* confidence scores
* volatility estimates
* prediction metadata
* regime classifications

## Owns

* inference execution
* prediction caching
* model loading
* preprocessing parity
* prediction serialization

## Does NOT Own

* model training
* dashboard rendering
* websocket ingestion
* feature generation

## Failure Modes

* model loading failures
* inference latency spikes
* stale predictions
* preprocessing mismatch
* invalid feature schemas

# API Service

## Responsibility

Expose system functionality through stable HTTP and WebSocket interfaces.

## Inputs

* prediction service outputs
* market state data
* monitoring metrics
* system metadata

## Outputs

* REST responses
* WebSocket streams
* JSON payloads
* monitoring endpoints

## Owns

* request validation
* response serialization
* endpoint routing
* authentication layers
* API observability

## Does NOT Own

* model training
* feature calculations
* realtime ingestion
* frontend rendering

## Failure Modes

* request timeouts
* invalid payloads
* stale cache responses
* websocket disconnects
* dependency service failures

# Dashboard

## Responsibility

Visualize realtime market intelligence, prediction states, and system observability.

## Inputs

* API responses
* WebSocket live streams
* prediction metrics
* monitoring metrics

## Outputs

* realtime charts
* prediction visualizations
* monitoring panels
* system health displays
* paper trading analytics

## Owns

* frontend rendering
* chart visualization
* UI state management
* realtime subscriptions
* operator-facing observability

## Does NOT Own

* ML inference
* model training
* feature engineering
* market ingestion

## Failure Modes

* websocket desynchronization
* stale UI state
* rendering lag
* chart synchronization issues
* failed API requests
