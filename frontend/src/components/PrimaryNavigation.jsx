import React from 'react';
import {NavLink} from 'react-router-dom';
import {House,Globe2,Plus,Users,Info} from 'lucide-react';

const destinations=[['/','Home',House],['/world','World',Globe2],['/launch','Launch',Plus],['/community','Community',Users],['/about','About',Info]];
export const PrimaryNavigation=({mobile=false})=><nav className={mobile?'mobile-navigation':'primary-navigation'} aria-label={mobile?'Mobile navigation':'Main navigation'} data-testid={mobile?'mobile-navigation':'primary-navigation'}>
 {destinations.map(([to,label,Icon])=><NavLink key={to} to={to} end={to==='/'} data-testid={`${mobile?'mobile':'nav'}-${label.toLowerCase()}`}><Icon size={17} strokeWidth={1.7}/><span>{label}</span></NavLink>)}
</nav>;