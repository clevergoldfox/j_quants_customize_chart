#property strict
#property script_show_inputs

/*
  JPStock_ImportCsv_OfflineChart.mq4

  Fixed HST writer for MT4 build 600+ / build 1470.

  IMPORTANT FIX:
    HST v401 rate record is 60 bytes.
    datetime must be written as 8 bytes, not 4 bytes.

  CSV format:
    Date,Time,Open,High,Low,Close,Volume
    2024.01.04,12:00,100,110,90,105,123456
*/

input string InpCsvFile = "JP4661_D1.csv";
input string InpOfflineSymbol = "JP4661";
input int    InpPeriodMinutes = 1440;  // D1
input int    InpDigits = 0;            // Japanese stock adjusted prices may have .5/.2

void WriteFixedString(int handle, string value, int fixed_size)
{
   int len = StringLen(value);
   for(int i = 0; i < fixed_size; i++)
   {
      int ch = 0;
      if(i < len)
         ch = StringGetCharacter(value, i);
      FileWriteInteger(handle, ch, CHAR_VALUE);
   }
}

void WriteHstHeader(int handle, string symbol, int period_minutes, int digits)
{
   // HST v401 header = 148 bytes
   FileWriteInteger(handle, 401, LONG_VALUE);                         // 4
   WriteFixedString(handle, "(C) JQuants MT4 Stock Importer", 64);     // 64
   WriteFixedString(handle, symbol, 12);                               // 12
   FileWriteInteger(handle, period_minutes, LONG_VALUE);               // 4
   FileWriteInteger(handle, digits, LONG_VALUE);                       // 4
   FileWriteInteger(handle, (int)TimeCurrent(), LONG_VALUE);           // 4
   FileWriteInteger(handle, (int)TimeCurrent(), LONG_VALUE);           // 4

   for(int i = 0; i < 13; i++)                                        // 52
      FileWriteInteger(handle, 0, LONG_VALUE);
}

void WriteRateRecord(int handle, datetime dt, double o, double h, double l, double c, long vol)
{
   /*
     HST v401 / build 600+ record = 60 bytes

     datetime time     8 bytes  IMPORTANT
     double open       8 bytes
     double high       8 bytes
     double low        8 bytes
     double close      8 bytes
     long tick_volume  8 bytes
     int spread        4 bytes
     long real_volume  8 bytes
   */

   FileWriteLong(handle, (long)dt);          // 8 bytes, not FileWriteInteger
   FileWriteDouble(handle, o, DOUBLE_VALUE);
   FileWriteDouble(handle, h, DOUBLE_VALUE);
   FileWriteDouble(handle, l, DOUBLE_VALUE);
   FileWriteDouble(handle, c, DOUBLE_VALUE);
   FileWriteLong(handle, vol);
   FileWriteInteger(handle, 0, LONG_VALUE);
   FileWriteLong(handle, vol);
}

bool ReadOneCsvRow(int h, datetime &dt, double &o, double &hi, double &lo, double &c, long &vol)
{
   if(FileIsEnding(h))
      return(false);

   string d = FileReadString(h);
   if(StringLen(d) < 8)
      return(false);

   string t = FileReadString(h);
   o = FileReadNumber(h);
   hi = FileReadNumber(h);
   lo = FileReadNumber(h);
   c = FileReadNumber(h);
   double v = FileReadNumber(h);

   dt = StringToTime(d + " 00:00");
   vol = (long)v;

   return(dt > 0);
}

void SkipCsvHeader(int h)
{
   while(!FileIsEnding(h))
   {
      FileReadString(h);
      if(FileIsLineEnding(h))
         break;
   }
}

void OnStart()
{
   ResetLastError();

   int csv = FileOpen(InpCsvFile, FILE_READ | FILE_CSV | FILE_ANSI, ',');
   if(csv == INVALID_HANDLE)
   {
      Print("Cannot open CSV: ", InpCsvFile, " error=", GetLastError());
      Print("Place CSV into: MT4 Data Folder > MQL4 > Files");
      return;
   }

   SkipCsvHeader(csv);

   string hstName = InpOfflineSymbol + IntegerToString(InpPeriodMinutes) + ".hst";

   int hst = FileOpenHistory(hstName, FILE_BIN | FILE_WRITE);
   if(hst == INVALID_HANDLE)
   {
      Print("Cannot open HST file: ", hstName, " error=", GetLastError());
      FileClose(csv);
      return;
   }

   WriteHstHeader(hst, InpOfflineSymbol, InpPeriodMinutes, InpDigits);

   int count = 0;
   datetime dt;
   double o, hi, lo, c;
   long vol;

   while(!FileIsEnding(csv))
   {
      if(ReadOneCsvRow(csv, dt, o, hi, lo, c, vol))
      {
         WriteRateRecord(hst, dt, o, hi, lo, c, vol);
         count++;
      }
   }

   FileFlush(hst);
   FileClose(csv);
   FileClose(hst);

   Print("Created offline HST: ", hstName, " records=", count);
   Print("HST record format: 60 bytes, datetime=8 bytes.");
   Print("Please close old JP4661 offline chart if opened, then open: File > Open Offline > ", InpOfflineSymbol, ",D1");
}
