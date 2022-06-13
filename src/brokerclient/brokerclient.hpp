#ifndef BROKER_CLIENT_H
#define BROKER_CLIENT_H

#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <vector>

#include <twsapi/EReader.h>
#include <twsapi/EReaderOSSignal.h>
#include <twsapi/EWrapper.h>
#include <twsapi/EClientSocket.h>

class BrokerClient : public EWrapper, public EClientSocket {

public:
  BrokerClient(const char* host, int port, int clientId = 0);
  ~BrokerClient();

  EReader* reader;
  EReaderOSSignal signal;

  // Event handling functions
  void accountDownloadEnd(const std::string& accountName) {};
  void accountSummary(int reqId, const std::string& account, const std::string& tag,
                      const std::string& value, const std::string& curency) {};
  void accountSummaryEnd(int reqId) {};
  void accountUpdateMulti(int reqId, const std::string& account, const std::string& modelCode,
                          const std::string& key, const std::string& value,
                          const std::string& currency) {};
  void accountUpdateMultiEnd(int reqId) {};
  void bondContractDetails(int reqId, const ContractDetails& contractDetails) {};
  void commissionReport(const CommissionReport& commissionReport) {};
  void completedOrder(const Contract& contract, const Order& order,
                      const OrderState& orderState) {};
  void completedOrdersEnd() {};
  void connectAck() {};
  void connectionClosed() {};
  void contractDetails(int reqId, const ContractDetails& contractDetails) {};
  void contractDetailsEnd(int reqId) {};
  void currentTime(long time);
  void deltaNeutralValidation(int reqId, const DeltaNeutralContract& deltaNeutralContract) {};
  void displayGroupList(int reqId, const std::string& groups) {};
  void displayGroupUpdated(int reqId, const std::string& contractInfo) {};
  void error(int id, int errorCode, const std::string& errorString,
             const std::string& advancedOrderRejectJson);
  void execDetails(int reqId, const Contract& contract, const Execution& execution) {};
  void execDetailsEnd(int reqId) {};
  void familyCodes(const std::vector<FamilyCode> &familyCodes) {};
  void fundamentalData(TickerId reqId, const std::string& data) {};
  void headTimestamp(int reqId, const std::string& headTimestamp) {};
  void histogramData(int reqId, const HistogramDataVector& data) {};
  void historicalData(TickerId reqId, const Bar& bar) {};
  void historicalDataEnd(int reqId, const std::string& startDateStr,
                         const std::string& endDateStr) {};
  void historicalDataUpdate(TickerId reqId, const Bar& bar) {};
  void historicalNews(int requestId, const std::string& time, const std::string& providerCode,
                      const std::string& articleId, const std::string& headline) {};
  void historicalNewsEnd(int requestId, bool hasMore) {};
  void historicalSchedule(int reqId, const std::string& startDateTime,
                          const std::string& endDateTime, const std::string& timeZone,
                          const std::vector<HistoricalSession>& sessions) {};
  void historicalTicks(int reqId, const std::vector<HistoricalTick> &ticks, bool done) {};
  void historicalTicksBidAsk(int reqId, const std::vector<HistoricalTickBidAsk> &ticks,
                             bool done) {};
  void historicalTicksLast(int reqId, const std::vector<HistoricalTickLast> &ticks, bool done) {};
  void managedAccounts(const std::string& accountsList) {};
  void marketDataType(TickerId reqId, int marketDataType) {};
  void marketRule(int marketRuleId, const std::vector<PriceIncrement> &priceIncrements) {};
  void mktDepthExchanges(const std::vector<DepthMktDataDescription> &depthMktDataDescriptions) {};
  void newsArticle(int requestId, int articleType, const std::string& articleText) {};
  void newsProviders(const std::vector<NewsProvider> &newsProviders) {};
  void nextValidId(OrderId orderId) {};
  void openOrder(OrderId orderId, const Contract&, const Order&, const OrderState&) {};
  void openOrderEnd() {};
  void orderBound(long long orderId, int apiClientId, int apiOrderId) {};
  void orderStatus(OrderId orderId, const std::string& status, Decimal filled, Decimal remaining,
                   double avgFillPrice, int permId, int parentId, double lastFillPrice,
                   int clientId, const std::string& whyHeld, double mktCapPrice) {};
  void pnl(int reqId, double dailyPnL, double unrealizedPnL, double realizedPnL) {};
  void pnlSingle(int reqId, Decimal pos, double dailyPnL, double unrealizedPnL, double realizedPnL,
                 double value) {};
  void position(const std::string& account, const Contract& contract, Decimal position,
                double avgCost) {};
  void positionEnd() {};
  void positionMulti(int reqId, const std::string& account, const std::string& modelCode,
                     const Contract& contract, Decimal pos, double avgCost) {};
  void positionMultiEnd(int reqId) {};
  void realtimeBar(TickerId reqId, long time, double open, double high, double low, double close,
                   Decimal volume, Decimal wap, int count) {};
  void receiveFA(faDataType pFaDataType, const std::string& cxml) {};
  void replaceFAEnd(int reqId, const std::string& text) {};
  void rerouteMktDataReq(int reqId, int conid, const std::string& exchange) {};
  void rerouteMktDepthReq(int reqId, int conid, const std::string& exchange) {};
  void scannerData(int reqId, int rank, const ContractDetails& contractDetails,
                   const std::string& distance, const std::string& benchmark,
                   const std::string& projection, const std::string& legsStr) {};
  void scannerDataEnd(int reqId) {};
  void scannerParameters(const std::string& xml) {};
  void securityDefinitionOptionalParameter(int reqId, const std::string& exchange,
                                           int underlyingConId, const std::string& tradingClass,
                                           const std::string& multiplier,
                                           const std::set<std::string>& expirations,
                                           const std::set<double>& strikes) {};
  void securityDefinitionOptionalParameterEnd(int reqId) {};
  void smartComponents(int reqId, const SmartComponentsMap& theMap) {};
  void softDollarTiers(int reqId, const std::vector<SoftDollarTier> &tiers) {};
  void symbolSamples(int reqId, const std::vector<ContractDescription> &contractDescriptions) {};
  void tickByTickAllLast(int reqId, int tickType, long time, double price, Decimal size,
                         const TickAttribLast& tickAttribLast, const std::string& exchange,
                         const std::string& specialConditions) {};
  void tickByTickBidAsk(int reqId, long time, double bidPrice, double askPrice, Decimal bidSize,
                        Decimal askSize, const TickAttribBidAsk& tickAttribBidAsk) {};
  void tickByTickMidPoint(int reqId, time_t time, double midPoint) {};
  void tickEFP(TickerId tickerId, TickType tickType, double basisPoints,
               const std::string& formattedBasisPoints, double totalDividends, int holdDays,
               const std::string& futureLastTradeDate, double dividendImpact,
               double dividendsToLastTradeDate) {};
  void tickGeneric(TickerId tickerId, TickType tickType, double value) {};
  void tickNews(int tickerId, time_t timeStamp, const std::string& providerCode,
                const std::string& articleId, const std::string& headline,
                const std::string& extraData) {};
  void tickOptionComputation(TickerId tickerId, TickType tickType, int tickAttrib,
                             double impliedVol, double delta, double optPrice, double pvDividend,
                             double gamma, double vega, double theta, double undPrice) {};
  void tickPrice(TickerId tickerId, TickType field, double price, const TickAttrib& attrib) {};
  void tickReqParams(int tickerId, double minTick, const std::string& bboExchange,
                     int snapshotPermissions) {};
  void tickSize(TickerId tickerId, TickType field, Decimal size) {};
  void tickSnapshotEnd(int reqId) {};
  void tickString(TickerId tickerId, TickType tickType, const std::string& value) {};
  void updateAccountTime(const std::string& timeStamp) {};
  void updateAccountValue(const std::string& key, const std::string& val,
                          const std::string& currency, const std::string& accountName) {};
  void updateMktDepth(TickerId id, int position, int operation, int side, double price,
                      Decimal size) {};
  void updateMktDepthL2(TickerId id, int position, const std::string& marketMaker, int operation,
                        int side, double price, Decimal size, bool isSmartDepth) {};
  void updateMktDepthL2(TickerId id, int position, const std::string& marketMaker, int operation,
                        int side, double price, int size, bool isSmartDepth) {};
  void updateNewsBulletin(int msgId, int msgType, const std::string& newsMessage,
                          const std::string& originExch) {};
  void updatePortfolio(const Contract& contract, Decimal position, double marketPrice,
                       double marketValue, double averageCost, double unrealizedPNL,
                       double realizedPNL, const std::string& accountName) {};
  void userInfo(int reqId, const std::string& whiteBrandingId) {};
  void verifyAndAuthCompleted(bool isSuccessful, const std::string& errorText) {};
  void verifyAndAuthMessageAPI(const std::string& apiData, const std::string& xyzChallange) {};
  void verifyCompleted(bool isSuccessful, const std::string& errorText) {};
  void verifyMessageAPI(const std::string& apiData) {};
  void winError(const std::string& str, int lastError) {};
  void wshEventData(int reqId, const std::string& dataJson) {};
  void wshMetaData(int reqId, const std::string& dataJson) {};


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
