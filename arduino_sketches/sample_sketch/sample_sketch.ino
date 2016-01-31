/*Freq in hertz*/
#define SAMP_FREQ 2000


long int ptime = 0;
long int ntime = 0;
long int samp_period = 0;
long int samp_delay = 0;

float val[3];
struct packet {
  uint32_t sof;
  uint32_t len;
  uint32_t crc;
  float val[3];
  uint32_t eof;
}pkt;



void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  analogReference(DEFAULT);
  samp_period = (long int)(((double)1 / (double)SAMP_FREQ) * 1000000);  //In microseconds
  samp_delay = samp_period;
  
  //Serial.print(samp_delay);
  //Serial.print("   ");
  /*Serial.print(samp_period);
  Serial.print("\n\r******** \n\r");
  */
}

void loop() {
  ntime = micros();
  /*
  Serial.print(samp_period);
  Serial.print("   ");
  Serial.print(samp_delay);
  Serial.print("   ");
  Serial.print(ntime-ptime);
  Serial.print("\n\r");
  */
  if ((ntime-ptime) >= samp_delay) {
    ptime = ntime;
    
    val[0] = ((5.0/1024) * analogRead(0));
    val[1] = ((5.0/1024) * analogRead(1));
    val[2] = ((5.0/1024) * analogRead(2));
  
    pkt.sof = 0xC0DEFACE;
    pkt.len = sizeof(pkt.val);
    pkt.crc = 0x00000000;
    pkt.val[0] = val[0];
    pkt.val[1] = val[1];
    pkt.val[2] = val[2];
    pkt.eof = 0xDA7C105E;
    
    
    Serial.write((uint8_t *)&pkt, sizeof(pkt));
    
    
    //Serial.print(samp_delay);
    //Serial.print("   ");
    //Serial.print(samp_period);
    //Serial.print("\n\r");
    
        
    samp_delay = samp_period;
    samp_delay -= (micros() - ntime); // this much time is already over
  }
  //delayMicroseconds(samp_delay);
  
}
