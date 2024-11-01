#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdint.h>
#include <time.h>
 
#define MAX_TRANSFER_SIZE 256            // Maximum transfer size (5 bytes)
 
// [2024-10-23 14:00] Modify SPI clock speed parsing to accept formats like 4.1M or 0.5K
 
double parse_clock_speed(const char *arg) {
    char *endptr;
    double speed = strtod(arg, &endptr);
 
    if (*endptr == 'M' || *endptr == 'm') {
        speed *= 1000000;
    } else if (*endptr == 'K' || *endptr == 'k') {
        speed *= 1000;
    }
    return speed;
}
 
int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <SPI device> <clock speed (Hz)> <data to send (up to 5 bytes in hex)> [<delay> <data to send> ...] \n"
                        "       %s /dev/spidev0.0 4.1M 0A1B2C [20 FFFFFFFFFF ...] \n", argv[0], argv[0]);
        return EXIT_FAILURE;
    }
 
    const char *spi_device = argv[1];
    double clock_speed = parse_clock_speed(argv[2]);
    int spi_fd;
    uint8_t tx_buffer[MAX_TRANSFER_SIZE] = {0};
    uint8_t rx_buffer[MAX_TRANSFER_SIZE] = {0};
 
    // Open SPI device file
    spi_fd = open(spi_device, O_RDWR);
    if (spi_fd < 0) {
        perror("Failed to open SPI device\n");
        return EXIT_FAILURE;
    }
 
    int arg_index = 3;
    while (arg_index < argc) {
        // Set data to be transmitted
        int data_len = strlen(argv[arg_index]);
        if (data_len > MAX_TRANSFER_SIZE * 2) {
            fprintf(stderr, "Error: Data to send exceeds maximum transfer size of %d bytes.\n", MAX_TRANSFER_SIZE);
            close(spi_fd);
            return EXIT_FAILURE;
        }
        for (int i = 0; i < data_len / 2; i++) {
            sscanf(&argv[arg_index][i * 2], "%2hhx", &tx_buffer[i]);
        }
        arg_index++;
 
        struct spi_ioc_transfer tr = {
            .tx_buf = (unsigned long)tx_buffer,
            .rx_buf = (unsigned long)rx_buffer,
            .len = data_len / 2,
            .delay_usecs = 0,
            .speed_hz = (uint32_t)clock_speed,
            .bits_per_word = 8,
        };
 
        // SPI transmit and receive
        if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
            perror("Failed to transfer SPI message\n");
            close(spi_fd);
            return EXIT_FAILURE;
        }
 
        // Delay if specified
        if (arg_index < argc && atoi(argv[arg_index]) > 0) {
            int delay_ns = atoi(argv[arg_index]);
            struct timespec req = {0};
            req.tv_sec = 0;
            req.tv_nsec = delay_ns;
            nanosleep(&req, NULL);
            arg_index++;
        }
 
        // Print transmitted and received data
        printf("<MOSI> ");
        for (int i = 0; i < data_len / 2; i++) {
            printf("%02X ", tx_buffer[i]);
        }
        printf("\n");
 
        printf("<MISO> ");
        for (int i = 0; i < data_len / 2; i++) {
            printf("%02X ", rx_buffer[i]);
        }
        printf("\n\n");
    }
 
    // Close SPI device file
    close(spi_fd);
    return EXIT_SUCCESS;
}
 
