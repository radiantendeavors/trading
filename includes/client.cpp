#ifndef TRADER_CLIENT_HPP
#def TRADER_CLIENT_HPP

#include <twsapi/EWrapper.h>
#include <twsapi/EReaderOSSignal.h>
#include <twsapi/EReader.h>
#include <twsapi/EWrapper_prototypes.h>

class EclientSocket;

class Client : public EWrapper {

  //
private:
  EReaderOSSignal m_osSignal;
  EClientSocket * const m_pClient;

  //
}

#endif
