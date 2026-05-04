#property strict
#property script_show_inputs

/*
  JPStock_ImportCsv_OfflineChart

  Purpose:
    Prototype script to read MQL4/Files/JP4661_D1.csv and create MT4 offline history file.

  Important:
    MT4 .hst behavior can vary by build/broker.
    Test on the target XMTrading MT4 build 1470 environment.

  CSV format:
    Date,Time,Open,High,Low,Close,Volume
    2024.01.04,00:00,100,110,90,105,123456

  Usage:
    1. Put JP4661_D1.csv into MQL4/Files.
    2. Compile this script in MetaEditor.
    3. Drag script onto any chart.
    4. Open File > Open Offline and select JP4661,D1 if generated.
*/

input string InpCsvFile = "JP4661_D1.csv";
input string InpOfflineSymbol = "JP4661";
input int    InpPeriodMinutes = 1440;     // D1
input int    InpDigits = 0;
input bool   InpOpenOfflineChart = false; // experimental

#pragma pack(push,1)
struct HstHeader
{
   int      version;
   char     copyright[64];
   char     symbol[12];
   int      period;
   int      digits;
   datetime timesign;
   datetime last_sync;
   int      unused[13];
};

struct RateRecord
{
   datetime ctm;
   double   open;
   double   high;
   double   low;
   double   close;
   long     tick_volume;
   int      spread;
   long     real_volume;
};
#pragma pack(pop)

void SetCharArray(char &arr[], string value, int size)
{
   ArrayInitialize(arr, 0);
   for(int i=0; i<StringLen(value) && i<size-1; i++)
      arr[i] = (char)StringGetCharacter(value, i);
}

bool ReadOneCsvRow(int h, datetime &dt, double &o, double &hi, double &lo, double &c, long &vol)
{
   if(FileIsEnding(h)) return(false);

   string d = FileReadString(h);
   if(FileIsEnding(h) && StringLen(d) == 0) return(false);

   string t = FileReadString(h);
   o = FileReadNumber(h);
   hi = FileReadNumber(h);
   lo = FileReadNumber(h);
   c = FileReadNumber(h);
   double v = FileReadNumber(h);

   if(StringLen(d) < 8) return(false);
   dt = StringToTime(d + " " + t);
   vol = (long)v;

   return(dt > 0);
}

void OnStart()
{
   int csv = FileOpen(InpCsvFile, FILE_READ|FILE_CSV|FILE_ANSI, ',');
   if(csv == INVALID_HANDLE)
   {
      Print("Cannot open CSV: ", InpCsvFile, " error=", GetLastError());
      return;
   }

   // Skip header line
   if(!FileIsEnding(csv))
   {
      string header = FileReadString(csv);
      while(!FileIsLineEnding(csv) && !FileIsEnding(csv))
         FileReadString(csv);
   }

   string hstName = InpOfflineSymbol + IntegerToString(InpPeriodMinutes) + ".hst";
   int hst = FileOpenHistory(hstName, FILE_BIN|FILE_WRITE);
   if(hst == INVALID_HANDLE)
   {
      Print("Cannot open HST file: ", hstName, " error=", GetLastError());
      FileClose(csv);
      return;
   }

   HstHeader header;
   header.version = 401;
   SetCharArray(header.copyright, "(C) JQuants MT4 Stock Importer", 64);
   SetCharArray(header.symbol, InpOfflineSymbol, 12);
   header.period = InpPeriodMinutes;
   header.digits = InpDigits;
   header.timesign = TimeCurrent();
   header.last_sync = TimeCurrent();

   FileWriteStruct(hst, header);

   int count = 0;
   datetime dt;
   double o, hi, lo, c;
   long vol;

   while(!FileIsEnding(csv))
   {
      if(!ReadOneCsvRow(csv, dt, o, hi, lo, c, vol))
         continue;

      RateRecord r;
      r.ctm = dt;
      r.open = o;
      r.high = hi;
      r.low = lo;
      r.close = c;
      r.tick_volume = vol;
      r.spread = 0;
      r.real_volume = vol;

      FileWriteStruct(hst, r);
      count++;
   }

   FileClose(csv);
   FileClose(hst);

   Print("Created offline HST: ", hstName, " records=", count);
   Print("Open MT4 menu: File > Open Offline > ", InpOfflineSymbol, ",D1");

   if(InpOpenOfflineChart)
   {
      Print("Auto open offline chart is not guaranteed on all MT4 builds. Please open manually if needed.");
   }
}
