void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

float val = 0;
int deg = 0;
void loop() {
  struct packet {
    uint32_t sof;
    uint32_t len;
    uint32_t crc;
    float val;
    uint32_t eof;
  }pkt;

  val = 5 * sin(0.0174532 * deg);
  deg = ((deg + 1) % 360);
  pkt.sof = 0xC0DEFACE;
  pkt.len = sizeof(pkt.val);
  pkt.crc = 0x00000000;
  pkt.val = val;
  pkt.eof = 0xDA7C105E;
  
  Serial.write((uint8_t *)&pkt, sizeof(pkt));
  //Serial.print(val);
  //Serial.print("\n\r");
/*
  uint8_t *a = (uint8_t *)&pkt;


  for (int i =0; i<sizeof(pkt); i++) {
    Serial.print(a[i], HEX);
    Serial.print(" ");
  }
  Serial.print("\n\r");
  */
  //delay(1);
}
