#ifndef BROKER_CLIENT_H
#define BROKER_CLIENT_H

#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <vector>

#include "twsapi/source/cppclient/client/EReader.h"
#include "twsapi/source/cppclient/client/EReaderOSSignal.h"
#include "twsapi/source/cppclient/client/EWrapper.h"
#include "twsapi/source/cppclient/client/EClientSocket.h"

template<class ItemType>
/***************************************************************************************************
 *
 * @class BrokerClient brokerclient.hpp "brokerclient/brokerclient.hpp"
 *
 * @param host
 * @param port
 * @param clientID
 *
 **************************************************************************************************/
class BrokerClient : public EWrapper, public EClientSocket {


public:
  BrokerClient(const char* host, int port, int clientId = 0);
  ~BrokerClient();

  EReader* reader;
  EReaderOSSignal signal;

  // Event handling functions
  /*************************************************************************************************
   *
   * accountDownloadEnd
   *
   * Notifies when all the account's information has finished.
   *
   * @param account The account's id.
   *
   ************************************************************************************************/
  void accountDownloadEnd(const std::string& account) {
    std::cout << "Download End for Account: " << account << std::endl;
  }

  /*************************************************************************************************
   *
   * accountSummary
   *
   * Receives the account information. This method will receive the account information just as it
   * appears in the TWS' Account Summary Window.
   *
   * @param reqId The request's unique id.
   * @param account The account id.
   * @param tag The account's attribute being received.
   *            - AccountType - Identifies the IB account structure.
   *            - NetLiquidation - The basis for determining the price of assets in your account.
   *                               Total cash value + stock value + options value + bond value
   *            - SettledCash    - Cash recognized at the time of settlement.
   *            ...
   *
   * @param value the account's attribuet's value
   * @param currency the currency on which the value is expressed
   *
   ************************************************************************************************/
  void acountSummary(int reqId,
                     const std::string& account,
                     const std::string& tag,
                     const std::string& value,
                     const std::string& curency) {
    std::cout << "Account: " << account << std::endl;
    std::cout << "Value: " << value << std::endl;
  }

  /*************************************************************************************************
   *
   * accountSummaryEnd
   *
   * Notifies when all the accounts' information has ben received. Requires TWS 967+ to receive
   * accountSummaryEnd in linked account structures.
   *
   * @param reqId
   *
   ************************************************************************************************/
  void accountSummaryEnd(int reqId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * accountUpdateMulti
   *
   * Provides the account updates.
   *
   * @param reqId
   * @param account
   * @param modelCode
   * @param key
   * @param value
   * @param currency
   *
   ************************************************************************************************/
  void accountUpdateMulti(int reqId,
                          const std::string& account,
                          const std::string& modelCode,
                          const std::string& key,
                          const std::string& value,
                          const std::string& currency) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * accountUpdateMultiEnd
   *
   * Indicates all the account updates have been transmitted.
   *
   * @param reqId
   *
   ************************************************************************************************/
  void accountUpdateMultiEnd(int reqId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * bondContractDetails
   *
   * Delivers the Bond contract data after this has been requested via reqContractDetails.
   *
   * @param reqId
   * @param contractDetails
   *
   ************************************************************************************************/
  void bondContractDetails(int reqId, const ContractDetails& contractDetails) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * commissionReport
   *
   * 
   *
   * @param commissionReport
   *
   ************************************************************************************************/
  void commissionReport(const CommissionReport& commissionReport) {
    std::cout << "Commission Report:" << std::endl;
  }

  /*************************************************************************************************
   *
   * completedOrder
   *
   * @param contract
   * @param order
   * @param orderState
   *
   ************************************************************************************************/
  void completedOrder(const Contract& contract,
                      const Order& order,
                      const OrderState& orderState) {
    std::cout << "Order Completed." << std::endl;
  }

  /*************************************************************************************************
   *
   * completedOrdersEnd
   *
   * Notifies the end of the completed orders' reception.
   *
   ************************************************************************************************/
  void completedOrdersEnd() {
    std::cout << "completedOrdersEnd" << std::endl;
  }

  /*************************************************************************************************
   *
   * connectAck
   *
   * Callback initially acknowledging connection attempt connection handshake not complete until
   * nextValidID is received
   *
   ************************************************************************************************/
  void connectAck() {
    std::cout << "connectionAck" << std::endl;
  }

  /*************************************************************************************************
   *
   * connectionClosed
   *
   * ...
   *
   ************************************************************************************************/
  void connectionClosed() {
    std::cout << "Connection Closed" << std::endl;
  }

  /*************************************************************************************************
   *
   * accountDownloadEnd
   *
   * @param reqId
   * @param contractDetails
   *
   ************************************************************************************************/
  void contractDetails(int reqId, const ContractDetails& contractDetails) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * accountDownloadEnd
   *
   * @param accountName
   *
   ************************************************************************************************/
    void contractDetailsEnd(int reqId) {};

  /*************************************************************************************************
   * currentTime
   * Receives and displays the current time.
   *
   * @param curTime Provides the current time from the server.
   *
   ************************************************************************************************/
  void currentTime(long curTime) {
    time_t epoch = curTime;
    std::cout << "Current time: " << asctime(localtime(&epoch)) << std::endl;
  }

  /*************************************************************************************************
   *
   * deltaNeutralValidation
   *
   * @param reqId
   * @param deltaNeutralContract
   *
   ************************************************************************************************/
  void deltaNeutralValidation(int reqId,
                              const DeltaNeutralContract& deltaNeutralContract) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * displayGroupList
   *
   * @param reqId
   * @param groups
   *
   ************************************************************************************************/
  void displayGroupList(int reqId, const std::string& groups) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * displayGroupUpdated
   *
   * @param reqId
   * @param contractInfo
   *
   ************************************************************************************************/
  void displayGroupUpdated(int reqId, const std::string& contractInfo) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * error
   *
   * Respond to errors
   *
   * @param id
   * @param code
   * @param msg
   * @param advancedOrderRejectJson
   *
   ************************************************************************************************/
  void error(int id,
             int code,
             const std::string& msg,
             const std::string& advancedOrderRejectJson) {
    std::cout << "Error: " << code << ": " << msg << std::endl;
  }

  /*************************************************************************************************
   *
   * execDetails
   *
   * @param reqId
   * @param contract
   * @param execution
   *
   ************************************************************************************************/
  void execDetails(int reqId,
                   const Contract& contract,
                   const Execution& execution) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * execDetailsEnd
   *
   * @param reqId
   *
   ************************************************************************************************/
  void execDetailsEnd(int reqId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * familyCodes
   *
   * @param familyCodes
   *
   ************************************************************************************************/
  void familyCodes(const std::vector<FamilyCode> &familyCodes) {
    std::cout << "Family Codes:" << std::endl;
  }

  /*************************************************************************************************
   *
   * fundamentalData
   *
   * @param reqId
   * @param data
   *
   ************************************************************************************************/
  void fundamentalData(TickerId reqId, const std::string& data) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * headTimestamp
   *
   * @param reqId
   * @param headTimestamp
   *
   ************************************************************************************************/
  void headTimestamp(int reqId, const std::string& headTimestamp) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * histogramData
   *
   * @param reqId
   * @param data
   *
   ************************************************************************************************/
  void histogramData(int reqId, const HistogramDataVector& data) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalData
   *
   * @param reqId
   * @param bar
   *
   ************************************************************************************************/
  void historicalData(TickerId reqId, const Bar& bar) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalDataEnd
   *
   * @param accountName
   *
   ************************************************************************************************/
  void historicalDataEnd(int reqId,
                         const std::string& startDateStr,
                         const std::string& endDateStr) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalDataUpdate
   *
   * @param accountName
   *
   ************************************************************************************************/
  void historicalDataUpdate(TickerId reqId, const Bar& bar) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalNews
   *
   * @param requestId
   * @param providerCode
   * @param articleId
   * @param headline
   *
   ************************************************************************************************/
  void historicalNews(int requestId,
                      const std::string& time,
                      const std::string& providerCode,
                      const std::string& articleId,
                      const std::string& headline) {
    std::cout << "Request ID: " << requestId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalNewsEnd
   *
   * @param requestId
   * @param hasMore
   *
   ************************************************************************************************/
  void historicalNewsEnd(int requestId, bool hasMore) {
    std::cout << "Request ID: " << requestId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalSchedule
   *
   * @param reqId
   * @param startDateTime
   * @param endDateTime
   * @param timeZone
   * @param sessions
   *
   ************************************************************************************************/
  void historicalSchedule(int reqId,
                          const std::string& startDateTime,
                          const std::string& endDateTime,
                          const std::string& timeZone,
                          const std::vector<HistoricalSession>& sessions) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalTicks
   *
   * @param reqId
   * @param &ticks
   * @param done
   *
   ************************************************************************************************/
  void historicalTicks(int reqId,
                       const std::vector<HistoricalTick> &ticks,
                       bool done) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalTicksBidAsk
   *
   * @param reqId
   * @param &ticks
   * @param done
   *
   ************************************************************************************************/
  void historicalTicksBidAsk(int reqId,
                             const std::vector<HistoricalTickBidAsk> &ticks,
                             bool done) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * historicalTicksLast
   *
   * @param reqId
   * @param &ticks
   * @param done
   *
   ************************************************************************************************/
  void historicalTicksLast(int reqId,
                           const std::vector<HistoricalTickLast> &ticks,
                           bool done) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * managedAccounts
   *
   * @param accountsList
   *
   ************************************************************************************************/
  void managedAccounts(const std::string& accountsList) {
    std::cout << "Account List: " << std::endl;
  }

  /*************************************************************************************************
   *
   * marketDataType
   *
   * @param reqId
   * @param marketDataType
   *
   ************************************************************************************************/
  void marketDataType(TickerId reqId, int marketDataType) {
    std::cout << "Market Data Type:" << std::endl;
  }

  /*************************************************************************************************
   *
   * marketRule
   *
   * @param marketRuleId
   * @param priceIncrements
   *
   ************************************************************************************************/
  void marketRule(int marketRuleId,
                  const std::vector<PriceIncrement> &priceIncrements) {
    std::cout << "Market Rule ID: " << marketRuleId << std::endl;
  }

  /*************************************************************************************************
   *
   * mktDepthExchanges
   *
   * @param depthMktDataDescriptions
   *
   ************************************************************************************************/
  void mktDepthExchanges(const std::vector<DepthMktDataDescription> &depthMktDataDescriptions) {
    std::cout << "Market Depth Exchanges: "<< std::endl;
  }

  /*************************************************************************************************
   *
   * newsArticle
   *
   * @param requestId
   * @param articleType
   * @param articleText
   *
   ************************************************************************************************/
  void newsArticle(int requestId, int articleType, const std::string& articleText) {
    std::cout << "Request ID: " << requestId << std::endl;
  }

  /*************************************************************************************************
   *
   * newsProviders
   *
   * @param newsProviders
   *
   ************************************************************************************************/
  void newsProviders(const std::vector<NewsProvider> &newsProviders) {
    std::cout << "News Providers:" << std::endl;
  }

  /*************************************************************************************************
   *
   * nextValidId
   *
   * @param orderId
   *
   ************************************************************************************************/
  void nextValidId(OrderId orderId) {
    std::cout << "Next Valid ID: " << std::endl;
  }

  /*************************************************************************************************
   *
   * openOrder
   *
   * @param orderId
   * @param Contract
   * @param Order
   * @param OrderState
   *
   ************************************************************************************************/
  void openOrder(OrderId orderId, const Contract&, const Order&, const OrderState&) {
    std::cout << "Order ID: " << std::endl;
  }

  /*************************************************************************************************
   *
   * openOrderEnd
   *
   * ...
   *
   ************************************************************************************************/
  void openOrderEnd() {
    std::cout << "Open Order End" << std::endl;
  }

  /*************************************************************************************************
   *
   * orderBound
   *
   * @param orderId
   * @param apiClientId
   * @param apiOrderId
   *
   ************************************************************************************************/
  void orderBound(long long orderId, int apiClientId, int apiOrderId) {
    std::cout << "Request ID: " << orderId << std::endl;
  }

  /*************************************************************************************************
   *
   * orderStatus
   *
   * @param orderId
   * @param status
   * @param filled
   * @param remaining
   * @param avgFillPrice
   * @param permId
   * @param parentId
   * @param lastFillPrice
   * @param clientId
   * @param whyHeld
   * @param mktCapPrice
   *
   ************************************************************************************************/
  void orderStatus(OrderId orderId,
                   const std::string& status,
                   Decimal filled,
                   Decimal remaining,
                   double avgFillPrice,
                   int permId,
                   int parentId,
                   double lastFillPrice,
                   int clientId,
                   const std::string& whyHeld,
                   double mktCapPrice) {
    std::cout << "Order ID: " << std::endl;
  }

  /*************************************************************************************************
   *
   * pnl
   *
   * @param reqId
   * @param dailyPnL
   * @param unrealizedPnL
   * @param realizedPnL
   *
   ************************************************************************************************/
  void pnl(int reqId, double dailyPnL, double unrealizedPnL, double realizedPnL) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * pnlSingle
   *
   * @param reqId
   * @param pos
   * @param dailyPnL
   * @param unrealizedPnL
   * @param realizedPnL
   * @param value
   *
   ************************************************************************************************/
  void pnlSingle(int reqId,
                 Decimal pos,
                 double dailyPnL,
                 double unrealizedPnL,
                 double realizedPnL,
                 double value) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * position
   *
   * @param account
   * @param contract
   * @param position
   * @param avgCost
   *
   ************************************************************************************************/
  void position(const std::string& account,
                const Contract& contract,
                Decimal position,
                double avgCost) {
    std::cout << "Position:" << std::endl;
  }

  /*************************************************************************************************
   *
   * positionEnd
   *
   * @param accountName
   *
   ************************************************************************************************/
  void positionEnd() {
    std::cout << "Position End" << std::endl;
  }

  /*************************************************************************************************
   *
   * positionMult
   *
   * @param reqId
   * @param account
   * @param modelCode
   * @param contract
   * @param pos
   * @param avgCost
   *
   ************************************************************************************************/
  void positionMulti(int reqId,
                     const std::string& account,
                     const std::string& modelCode,
                     const Contract& contract,
                     Decimal pos,
                     double avgCost) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * positionMultiEnd
   *
   * @param reqId
   *
   ************************************************************************************************/
  void positionMultiEnd(int reqId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * accountDownloadEnd
   *
   * @param accountName
   *
   ************************************************************************************************/
  void realtimeBar(TickerId reqId,
                   long time,
                   double open,
                   double high,
                   double low,
                   double close,
                   Decimal volume,
                   Decimal wap,
                   int count) {
    std::cout << "Real Time Bar: " << std::endl;
  }

  /*************************************************************************************************
   *
   * receiveFA
   *
   * @param pFaDataType
   * @param cxml
   *
   ************************************************************************************************/
  void receiveFA(faDataType pFaDataType, const std::string& cxml) {
    std::cout << "Receive FA" << std::endl;
  }

  /*************************************************************************************************
   *
   * replaceFAEnd
   *
   * @param reqId
   * @param text
   *
   ************************************************************************************************/
  void replaceFAEnd(int reqId, const std::string& text) {
    std::cout << "Receive FA End: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * rerouteMktDataReq
   *
   * @param reqId
   * @param conid
   * @param exchange
   *
   ************************************************************************************************/
  void rerouteMktDataReq(int reqId, int conid, const std::string& exchange) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * rerouteMktDepthReq
   *
   * @param reqId
   * @param conid
   * @param exchange
   *
   ************************************************************************************************/
  void rerouteMktDepthReq(int reqId, int conid, const std::string& exchange) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * scannerData
   *
   * @param reqId
   * @param rank
   * @param contractDetails
   * @param distance
   * @param benchmark
   * @param projection
   * @param legsStr
   *
   ************************************************************************************************/
  void scannerData(int reqId,
                   int rank,
                   const ContractDetails& contractDetails,
                   const std::string& distance,
                   const std::string& benchmark,
                   const std::string& projection,
                   const std::string& legsStr) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * scannerDataEnd
   *
   * @param reqId
   *
   ************************************************************************************************/
  void scannerDataEnd(int reqId) {
    std::cout << "End Scanner Data For Request Id  " << reqId << "." << std::endl;
  }

  /*************************************************************************************************
   *
   * scannerParameters
   *
   * @param xml
   *
   ************************************************************************************************/
  void scannerParameters(const std::string& xml) {
    std::cout << "Scanner Parameters:  " << std::endl;
  }

  /*************************************************************************************************
   *
   * securityDefinitionOptionalParameter
   *
   * @param reqId
   * @param exchange
   * @param underlyingConId
   * @param tradingClass
   * @param multiplier
   * @param expirations
   * @param strikes
   *
   ************************************************************************************************/
  void securityDefinitionOptionalParameter(int reqId,
                                           const std::string& exchange,
                                           int underlyingConId,
                                           const std::string& tradingClass,
                                           const std::string& multiplier,
                                           const std::set<std::string>& expirations,
                                           const std::set<double>& strikes) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * securityDefinitionOptionalParameterEnd
   *
   * @param reqId
   *
   ************************************************************************************************/
  void securityDefinitionOptionalParameterEnd(int reqId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * smartComponents
   *
   * @param reqId
   * @param theMap
   *
   ************************************************************************************************/
  void smartComponents(int reqId, const SmartComponentsMap& theMap) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * softDollarTiers
   *
   * @param reqId
   * @param tiers
   *
   ************************************************************************************************/
  void softDollarTiers(int reqId, const std::vector<SoftDollarTier> &tiers) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * symbolSamples
   *
   * @param reqId
   * @param contractDescriptions
   *
   ************************************************************************************************/
  void symbolSamples(int reqId, const std::vector<ContractDescription> &contractDescriptions) {
    std::cout << "Request ID: " << reqId << std::endl;
    std::cout << "Number of descriptions: " << contractDescriptions.size() << std::endl;
    for (ContractDescription desc: contractDescriptions) {
      std::cout << "Symbol: " << desc.contract.symbol << std::endl;
    }
  }

  /*************************************************************************************************
   *
   * tickByTickAllLast
   *
   * @param reqId
   * @param tickType
   * @param time
   * @param price
   * @param size
   * @param tickAttribLast
   * @param exchange
   * @param specialConditions
   *
   ************************************************************************************************/
  void tickByTickAllLast(int reqId,
                         int tickType,
                         long time,
                         double price,
                         Decimal size,
                         const TickAttribLast& tickAttribLast,
                         const std::string& exchange,
                         const std::string& specialConditions) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * tickByTickBidAsk
   *
   * @param reqId
   * @param time
   * @param bidPrice
   * @param askPrice
   * @param bidSize
   * @param askSize
   * @param tickAttribBidAsk
   *
   ************************************************************************************************/
  void tickByTickBidAsk(int reqId,
                        long time,
                        double bidPrice,
                        double askPrice,
                        Decimal bidSize,
                        Decimal askSize,
                        const TickAttribBidAsk& tickAttribBidAsk) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * tickByTickMidPoint
   *
   * @param reqId
   * @param time
   * @param midPoint
   *
   ************************************************************************************************/
  void tickByTickMidPoint(int reqId,
                          time_t time,
                          double midPoint) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * tickEFP
   *
   * @param reqId
   * @param tickType
   * @param basisPoints
   * @param formattedBasisPoints
   * @param totalDividends
   * @param holdDays
   * @param futureLastTradeDate
   * @param dividendImpact
   * @param dividendsToLastTradeDate
   *
   ************************************************************************************************/
  void tickEFP(TickerId tickerId,
               TickType tickType,
               double basisPoints,
               const std::string& formattedBasisPoints,
               double totalDividends,
               int holdDays,
               const std::string& futureLastTradeDate,
               double dividendImpact,
               double dividendsToLastTradeDate) {
    std::cout << "Tick EFP" << std::endl;
  }

  /*************************************************************************************************
   *
   * tickGeneric
   *
   * @param tickerId
   * @param tickType
   * @param value
   *
   ************************************************************************************************/
  void tickGeneric(TickerId tickerId, TickType tickType, double value) {
    std::cout << "Tick Generic" << std::endl;
  }

  /*************************************************************************************************
   *
   * tickNews
   *
   * @param tickerId
   * @param timeStamp
   * @param providerCode
   * @param articleId
   * @param headline
   * @param extraData
   *
   ************************************************************************************************/
  void tickNews(int tickerId,
                time_t timeStamp,
                const std::string& providerCode,
                const std::string& articleId,
                const std::string& headline,
                const std::string& extraData) {
    std::cout << "Ticker ID: " << tickerId << std::endl;
  }

  /*************************************************************************************************
   *
   * tickOptionComputation
   *
   * @param tickerId
   * @param tickType
   * @param impliedVol
   * @param delta
   * @param optPrice
   * @param pvDividend
   * @param gamma
   * @param vega
   * @param theta
   * @param undPrice
   *
   ************************************************************************************************/
  void tickOptionComputation(TickerId tickerId,
                             TickType tickType,
                             int tickAttrib,
                             double impliedVol,
                             double delta,
                             double optPrice,
                             double pvDividend,
                             double gamma,
                             double vega,
                             double theta,
                             double undPrice) {
    std::cout << "Tick Option Computation:" << std::endl;
  }

  /*************************************************************************************************
   *
   * tickPrice
   *
   * @param tickerId
   * @param field
   * @param price
   * @param attrib
   *
   ************************************************************************************************/
  void tickPrice(TickerId tickerId,
                 TickType field,
                 double price,
                 const TickAttrib& attrib) {
    std::cout << "Tick Price: " << std::endl;
  }

  /*************************************************************************************************
   *
   * tickReqParams
   *
   * @param tickerId
   * @param minTick
   * @param bboExchange
   * @param snapshotPermissions
   *
   ************************************************************************************************/
  void tickReqParams(int tickerId,
                     double minTick,
                     const std::string& bboExchange,
                     int snapshotPermissions) {
    std::cout << "Ticker ID: " << tickerId << std::endl;
  }

  /*************************************************************************************************
   *
   * tickSize
   *
   * @param tickerId
   * @param field
   * @param size
   *
   ************************************************************************************************/
  void tickSize(TickerId tickerId, TickType field, Decimal size) {
    std::cout << "Tick Size:" << std::endl;
  }

  /*************************************************************************************************
   *
   * tickSnapshotEnd
   *
   * @param reqId
   *
   ************************************************************************************************/
  void tickSnapshotEnd(int reqId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * tickString
   *
   * @param tickerId
   *
   ************************************************************************************************/
  void tickString(TickerId tickerId, TickType tickType, const std::string& value) {
    std::cout << "Tick String." << std::endl;
  }

  /*************************************************************************************************
   *
   * updateAccountTime
   *
   * @param timeStamp
   *
   ************************************************************************************************/
  void updateAccountTime(const std::string& timeStamp) {
    std::cout << "Update Account Time." << std::endl;
  }

  /*************************************************************************************************
   *
   * updateAccountValue
   *
   * @param key
   *
   ************************************************************************************************/
  void updateAccountValue(const std::string& key,
                          const std::string& val,
                          const std::string& currency,
                          const std::string& accountName) {
    std::cout << "Update Account Value" << std::endl;
  }

  /*************************************************************************************************
   *
   * updateMktDepth
   *
   * @param id
   *
   ************************************************************************************************/
  void updateMktDepth(TickerId id,
                      int position,
                      int operation,
                      int side,
                      double price,
                      Decimal size) {
    std::cout << "Update Market Depth" << std::endl;
  }

  /*************************************************************************************************
   *
   * updateMktDepthL2
   *
   * @param id
   * @param position
   * @param marketMaker
   * @param operation
   * @param side
   * @param price
   * @param size
   * @param isSmartDepth
   *
   ************************************************************************************************/
  void updateMktDepthL2(TickerId id,
                        int position,
                        const std::string& marketMaker,
                        int operation,
                        int side,
                        double price,
                        Decimal size,
                        bool isSmartDepth) {
    std::cout << "Update Market Depth L2: " << std::endl;
  }

  /*************************************************************************************************
   *
   * updateNewsBulletin
   *
   * @param msgId
   * @param msgType
   * @param newsMessage
   * @param originExch
   *
   ************************************************************************************************/
  void updateNewsBulletin(int msgId,
                          int msgType,
                          const std::string& newsMessage,
                          const std::string& originExch) {
    std::cout << "Message ID: " << msgId << std::endl;
  }

  /*************************************************************************************************
   *
   * updatePortfolio
   *
   * @param contract
   * @param position
   * @param marketPrice
   * @param marketValue
   * @param averageCost
   * @param unrealizedPNL
   * @param realizedPNL
   * @param accountName
   *
   ************************************************************************************************/
  void updatePortfolio(const Contract& contract,
                       Decimal position,
                       double marketPrice,
                       double marketValue,
                       double averageCost,
                       double unrealizedPNL,
                       double realizedPNL,
                       const std::string& accountName) {
    std::cout << "Update Portfolio:" << std::endl;
  }

  /*************************************************************************************************
   *
   * userInfo
   *
   * @param reqId
   * @param whiteBrandingId
   *
   ************************************************************************************************/
  void userInfo(int reqId, const std::string& whiteBrandingId) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * verifyAndAuthCompleted
   *
   * @param isSuccessful
   * @param errorText
   *
   ************************************************************************************************/
  void verifyAndAuthCompleted(bool isSuccessful, const std::string& errorText) {
    if (isSuccessful) {
      std::cout << "Success" << std::endl;
    } else {
      std::cout << "Failed" << std::endl;
      //std::cout << "Error Message: " << errorText << std::endl;
    }
  }

  /*************************************************************************************************
   *
   * verifyAndAuthMessageAPI
   *
   * @param apiData
   * @param xyzChallange
   *
   ************************************************************************************************/
  void verifyAndAuthMessageAPI(const std::string& apiData,
                               const std::string& xyzChallange) {
    std::cout << "Verify And Auth Message API" << std::endl;
  }

  /*************************************************************************************************
   *
   * verifyCompleted
   *
   * @param isSuccessful
   * @param errorText
   *
   ************************************************************************************************/
  void verifyCompleted(bool isSuccessful, const std::string& errorText) {
    if (isSuccessful) {
      std::cout << "Success" << std::endl;
    } else {
      std::cout << "Failed" << std::endl;
      //std::cout << "Error Message: " << errorText << std::endl;
    }
  }

  /*************************************************************************************************
   *
   * verifyMessageAPI
   *
   * @param apiData
   *
   ************************************************************************************************/
  void verifyMessageAPI(const std::string& apiData) {
    std::cout << "Verify Message API: " << std::endl;
  }

  /*************************************************************************************************
   *
   * winError
   *
   * @param str
   * @param lastError
   *
   ************************************************************************************************/
  void winError(const std::string& str, int lastError) {
    std::cout << "String: " << str << std::endl;
    std::cout << "Last Error: " << lastError << std::endl;
  }

  /*************************************************************************************************
   *
   * accountDownloadEnd
   *
   * @param reqId
   * @param dataJson
   *
   ************************************************************************************************/
  void wshEventData(int reqId, const std::string& dataJson) {
    std::cout << "Request ID: " << reqId << std::endl;
  }

  /*************************************************************************************************
   *
   * wshMetaData
   *
   * @param reqId
   * @param dataJson
   *
   ************************************************************************************************/
  void wshMetaData(int reqId, const std::string& dataJson) {
    std::cout << "Request Id: " << reqId << std::endl;
  }

  void pnlOperation();
  void pnlSingleOperation();
	void tickDataOperation();
	void tickOptionComputationOperation();
	void delayedTickDataOperation();
	void marketDepthOperations();
	void realTimeBars();
	void marketDataType();
	void historicalDataRequests();
	void optionsOperations();
	void accountOperations();
	void orderOperations();
	void ocaSamples();
	void conditionSamples();
	void bracketSample();
	void hedgeSample();
	void contractOperations();
	void marketScanners();
	void fundamentals();
	void bulletins();
	void testAlgoSamples();
	void financialAdvisorOrderSamples();
	void financialAdvisorOperations();
	void testDisplayGroups();
	void miscelaneous();
	void reqFamilyCodes();
	void reqMatchingSymbols();
	void reqMktDepthExchanges();
	void reqNewsTicks();
	void reqSmartComponents();
	void reqNewsProviders();
	void reqNewsArticle();
	void reqHistoricalNews();
	void reqHeadTimestamp();
	void reqHistogramData();
	void rerouteCFDOperations();
	void marketRuleOperations();
	void continuousFuturesOperations();
  void reqHistoricalTicks();
  void reqTickByTickData();
	void whatIfSamples();
	void reqCurrentTime();
};

#endif // BROKER_CLIENT_H
