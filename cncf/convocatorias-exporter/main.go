// Convocatorias Prometheus Exporter
// Exports educational metrics for Convocatorias Platform

package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Metrics definitions
var (
	convocatoriasCreated = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "convocatorias_created_total",
			Help: "Total convocatorias created by tenant",
		},
		[]string{"tenant", "type"},
	)

	participationRate = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "convocatorias_participation_rate",
			Help: "Participation rate per tenant (0-1)",
		},
		[]string{"tenant"},
	)

	timeSavedHours = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "convocatorias_time_saved_hours",
			Help: "Hours saved per tenant",
		},
		[]string{"tenant"},
	)

	ltiLaunches = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "convocatorias_lti_launches_total",
			Help: "LTI launches by LMS",
		},
		[]string{"tenant", "lms"},
	)

	xapiStatements = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "convocatorias_xapi_statements_total",
			Help: "xAPI statements sent",
		},
		[]string{"tenant"},
	)

	apiLatency = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "convocatorias_api_latency_seconds",
			Help:    "API response latency",
			Buckets: []float64{0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0},
		},
		[]string{"endpoint"},
	)
)

func init() {
	prometheus.MustRegister(convocatoriasCreated)
	prometheus.MustRegister(participationRate)
	prometheus.MustRegister(timeSavedHours)
	prometheus.MustRegister(ltiLaunches)
	prometheus.MustRegister(xapiStatements)
	prometheus.MustRegister(apiLatency)
}

func fetchMetrics(apiURL, apiKey string) map[string]interface{} {
	start := time.Now()
	
	req, err := http.NewRequest("GET", apiURL+"/tenant/metrics", nil)
	if err != nil {
		log.Printf("Error creating request: %v", err)
		return nil
	}
	req.Header.Set("Authorization", "Bearer "+apiKey)
	
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("Error fetching metrics: %v", err)
		apiLatency.WithLabelValues("/tenant/metrics").Observe(time.Since(start).Seconds())
		return nil
	}
	defer resp.Body.Close()
	
	var metrics map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&metrics); err != nil {
		log.Printf("Error parsing metrics: %v", err)
		return nil
	}
	
	apiLatency.WithLabelValues("/tenant/metrics").Observe(time.Since(start).Seconds())
	return metrics
}

func updatePrometheusMetrics(metrics map[string]interface{}) {
	// Example tenant metrics - in production fetch all tenants
	tenants := []string{"demo-tenant"}
	
	for _, tenant := range tenants {
		// Mock data - replace with actual API calls
		participationRate.WithLabelValues(tenant).Set(0.85)
		timeSavedHours.WithLabelValues(tenant).Set(7.2)
		
		if m, ok := metrics["convocatorias_mes"].(float64); ok {
			convocatoriasCreated.WithLabelValues(tenant, "academic").Add(m)
		}
	}
}

func main() {
	var (
		port    = flag.String("port", "8000", "Port to expose metrics")
		apiURL  = flag.String("api-url", "", "Convocatorias API URL")
		apiKey  = flag.String("api-key", "", "API key for authentication")
		refresh = flag.Duration("refresh", 30*time.Second, "Refresh interval")
	)
	flag.Parse()

	if *apiURL == "" {
		*apiURL = os.Getenv("CONVOCATORIAS_API_URL")
	}
	if *apiKey == "" {
		*apiKey = os.Getenv("CONVOCATORIAS_API_KEY")
	}

	// Start metrics collection goroutine
	go func() {
		for {
			metrics := fetchMetrics(*apiURL, *apiKey)
			if metrics != nil {
				updatePrometheusMetrics(metrics)
			}
			time.Sleep(*refresh)
		}
	}()

	// Expose metrics endpoint
	http.Handle("/metrics", promhttp.Handler())
	log.Printf("Starting convocatorias-exporter on port %s", *port)
	log.Fatal(http.ListenAndServe(":"+*port, nil))
}