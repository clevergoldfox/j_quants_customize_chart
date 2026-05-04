#property strict
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_color1 DodgerBlue
#property indicator_width1 2

/*
  JPStock_CloseLine_FromCsv

  Simple fallback indicator:
  Reads CSV from MQL4/Files and plots close prices as a line on the current chart.

  This does NOT create a real candle chart.
  Use this as a backup/test view.
*/

input string InpCsvFile = "JP4661_D1.csv";

double CloseBuffer[];

int OnInit()
{
   SetIndexStyle(0, DRAW_LINE);
   SetIndexBuffer(0, CloseBuffer);
   IndicatorShortName("JP Stock Close from CSV: " + InpCsvFile);
   ArraySetAsSeries(CloseBuffer, true);
   return(INIT_SUCCEEDED);
}

int OnCalculate(
   const int rates_total,
   const int prev_calculated,
   const datetime &time[],
   const double &open[],
   const double &high[],
   const double &low[],
   const double &close[],
   const long &tick_volume[],
   const long &volume[],
   const int &spread[]
)
{
   for(int i=0; i<rates_total; i++)
      CloseBuffer[i] = EMPTY_VALUE;

   int handle = FileOpen(InpCsvFile, FILE_READ|FILE_CSV|FILE_ANSI, ',');
   if(handle == INVALID_HANDLE)
   {
      Print("Cannot open CSV: ", InpCsvFile, " error=", GetLastError());
      return(rates_total);
   }

   // header
   if(!FileIsEnding(handle))
   {
      for(int h=0; h<7 && !FileIsLineEnding(handle); h++)
         FileReadString(handle);
   }

   datetime dates[];
   double closes[];
   ArrayResize(dates, 0);
   ArrayResize(closes, 0);

   while(!FileIsEnding(handle))
   {
      string d = FileReadString(handle);
      string t = FileReadString(handle);
      double o = FileReadNumber(handle);
      double hi = FileReadNumber(handle);
      double lo = FileReadNumber(handle);
      double c = FileReadNumber(handle);
      double v = FileReadNumber(handle);

      if(StringLen(d) < 8) continue;

      datetime dt = StringToTime(d + " " + t);
      int n = ArraySize(dates);
      ArrayResize(dates, n+1);
      ArrayResize(closes, n+1);
      dates[n] = dt;
      closes[n] = c;
   }
   FileClose(handle);

   for(int bar=0; bar<rates_total; bar++)
   {
      datetime bt = time[bar];
      for(int j=ArraySize(dates)-1; j>=0; j--)
      {
         if(dates[j] == bt)
         {
            CloseBuffer[bar] = closes[j];
            break;
         }
      }
   }

   return(rates_total);
}
