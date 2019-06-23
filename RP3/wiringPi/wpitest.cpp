#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <wiringPi.h>

#include "wpitest.h"

int bitlist[9]={21,20,16,12,26,19,13,6,5};

#define MA_SIZE 5
double hz_data[N_SAMPLE];

double ave_hz;
double high_hz;
double low_hz;

double read_hz()
{
	int npulse=0;
	digitalWrite(GPIO17,0);
	while(digitalRead(GPIO18) == 0){
		usleep(4000);
	}

	for(int i=0;i<9;i++){
		npulse=npulse*2+digitalRead(bitlist[i]);
	};
	digitalWrite(GPIO17,1);
	if(npulse > 255){
		npulse = 19968 - 512 + npulse;
	}
	else {
		npulse = 19968 + npulse;
	}
	double hz = MASTER_CLK/(double)npulse;
	return hz;
}

void do_average()
{
	ave_hz=0;
	high_hz=0.0;
	low_hz=100.0;

	for(int i=0;i<N_SAMPLE;i++)
		hz_data[i]=read_hz();
	
	for(int i=0;i<N_SAMPLE;i++)
		ave_hz += hz_data[i];
	ave_hz /= (double)N_SAMPLE;

	for(int i=0;i<N_SAMPLE-MA_SIZE;i++){
		double ma_hz=0;
		for(int j=0;j<MA_SIZE;j++)
			ma_hz += hz_data[i+j];
		ma_hz /= (double)MA_SIZE;
		if(high_hz < ma_hz)
			high_hz = ma_hz;
		if(low_hz > ma_hz)
			low_hz = ma_hz;
	}
}


int main(int argc, char *argv[])
{
	if(wiringPiSetupGpio() == -1){
		printf("Wiring pi not ready");
		return -1;
	};
	pinMode(GPIO17,OUTPUT);
	pinMode(GPIO18,INPUT);
	digitalWrite(GPIO17,1);
	for(int i=0;i<9;i++){
		pinMode(bitlist[i],INPUT);
	};
	usleep(10000);	// sleep 10ms
	do_average();
	printf("%g,%g,%g",ave_hz, low_hz, high_hz);
	return 0;
}
		
