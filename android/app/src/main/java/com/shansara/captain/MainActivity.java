package com.shansara.captain;

import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private SharedPreferences prefs;
    private static final String PREF_NAME = "ShansaraCaptainPrefs";
    private static final String KEY_SERVER_IP = "server_ip";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Keep screen on while taking orders
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        prefs = getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);

        swipeRefresh = new SwipeRefreshLayout(this);
        webView = new WebView(this);
        swipeRefresh.addView(webView);
        setContentView(swipeRefresh);

        initWebViewSettings();

        swipeRefresh.setOnRefreshListener(() -> webView.reload());

        loadCaptainUrl();
    }

    private void initWebViewSettings() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadsImagesAutomatically(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                swipeRefresh.setRefreshing(false);
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                swipeRefresh.setRefreshing(false);
                showIpConfigDialog("Connection Error: " + description);
            }
        });
    }

    private void loadCaptainUrl() {
        String savedIp = prefs.getString(KEY_SERVER_IP, "");
        if (savedIp.isEmpty()) {
            showIpConfigDialog("Welcome to Shansara Captain. Please enter your Main Billing PC IP address (e.g. 192.168.1.5:8000):");
        } else {
            String url = "http://" + savedIp + "/captain";
            webView.loadUrl(url);
        }
    }

    private void showIpConfigDialog(String message) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Shansara POS Connection");
        builder.setMessage(message);

        final EditText input = new EditText(this);
        input.setHint("e.g. 192.168.1.5:8000");
        input.setText(prefs.getString(KEY_SERVER_IP, "192.168.1.5:8000"));
        builder.setView(input);

        builder.setPositiveButton("Connect", (dialog, which) -> {
            String ip = input.getText().toString().trim();
            if (!ip.isEmpty()) {
                prefs.edit().putString(KEY_SERVER_IP, ip).apply();
                Toast.makeText(MainActivity.this, "Connecting to " + ip + "...", Toast.LENGTH_SHORT).show();
                loadCaptainUrl();
            }
        });

        builder.setNegativeButton("Configure Later", (dialog, which) -> dialog.cancel());
        builder.setCancelable(false);
        builder.show();
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
