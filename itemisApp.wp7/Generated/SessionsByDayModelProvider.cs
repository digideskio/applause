using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using System.Collections.ObjectModel;
using System.Net;
using System.Linq;
using System.Xml.Linq;

namespace ItemisApp
{
	public class SessionsByDayModelProvider
	{
		
		private String day;

		public SessionsByDayModelProvider(String day)
		{
			this.day = day;
			this.Sessions = new ObservableCollection<Session>();
		}
				
		
		public ObservableCollection<Session> Sessions { get; private set; }
		
		public bool IsDataLoaded
		{
			get;
			private set;
		}
		
		public void LoadData()
		{
			WebClient client = new WebClient();
			client.DownloadStringAsync(new Uri("http://192.168.210.1:3000" + "/sessions/day/" + day + ".xml"));
			client.DownloadStringCompleted += new DownloadStringCompletedEventHandler(client_DownloadStringCompleted);			
		}
		
		void client_DownloadStringCompleted(object sender, DownloadStringCompletedEventArgs e)
		{
			if (e.Error == null)
			{
				ParseDataFromXml(e.Result);
				this.IsDataLoaded = true;
			}
		}

		void ParseDataFromXml(String source)
		{
			this.Sessions.Clear();

			XDocument xdoc = XDocument.Parse(source);
			XNamespace dc ="http://purl.org/dc/elements/1.1/";
			List<Session> result =
				(
					from session in xdoc.Descendants("session")
					select new Session
					{
						Id = session.Element("id").Value,
						Title = session.Element("title").Value,
						Description = session.Element("description").Value,
						Timeslot = session.Element("timeslot").Value,
						Room = session.Element("room").Value,
						Speakers = 
							(
								from speaker in xdoc.Descendants("speakers")
								select new Speaker
								{
									Id = speaker.Element("id").Value,
									Name = speaker.Element("name").Value,
									Bio = speaker.Element("bio").Value,
									Pictureurl = speaker.Element("pictureurl").Value,
								}
							).ToList<Speaker>(),

					}
				).ToList<Session>();
			result.ForEach(this.Sessions.Add);
		}
	}
}