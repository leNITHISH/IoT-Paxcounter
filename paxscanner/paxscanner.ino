#include "esp_wifi.h"
#include <Arduino.h>

// Minimal 802.11 management frame header
typedef struct {
  uint8_t frame_ctrl[2];
  uint8_t duration[2];
  uint8_t da[6];
  uint8_t sa[6];    // source MAC (the phone)
  uint8_t bssid[6];
  uint8_t seq_frag[2];
} __attribute__((packed)) mgmt_frame_t;

void IRAM_ATTR wifi_sniffer_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
  if (type != WIFI_PKT_MGMT) return;

  const wifi_promiscuous_pkt_t *ppkt = (wifi_promiscuous_pkt_t *)buf;
  const mgmt_frame_t *frame          = (mgmt_frame_t *)ppkt->payload;

  uint8_t ftype    = (frame->frame_ctrl[0] >> 2) & 0x03;
  uint8_t fsubtype = (frame->frame_ctrl[0] >> 4) & 0x0F;

  // Management (0) + Probe Request (4) only
  if (ftype != 0 || fsubtype != 4) return;

  int8_t  rssi = ppkt->rx_ctrl.rssi;
  uint8_t ch   = ppkt->rx_ctrl.channel;

  Serial.printf(
    "{\"mac\":\"%02X:%02X:%02X:%02X:%02X:%02X\",\"rssi\":%d,\"ch\":%d}\n",
    frame->sa[0], frame->sa[1], frame->sa[2],
    frame->sa[3], frame->sa[4], frame->sa[5],
    rssi, ch
  );
}

void setup() {
  Serial.begin(115200);
  delay(200);

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  esp_wifi_init(&cfg);
  esp_wifi_set_storage(WIFI_STORAGE_RAM);
  esp_wifi_set_mode(WIFI_MODE_NULL);
  esp_wifi_start();
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_promiscuous_rx_cb(wifi_sniffer_cb);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);

  Serial.println("{\"status\":\"PAX SCANNER READY\"}");
}

uint8_t cur_ch    = 1;
unsigned long last_hop = 0;

void loop() {
  // Hop channels every 150ms to catch more probes
  unsigned long now = millis();
  if (now - last_hop >= 150) {
    last_hop = now;
    cur_ch   = (cur_ch % 13) + 1;
    esp_wifi_set_channel(cur_ch, WIFI_SECOND_CHAN_NONE);
  }
}
